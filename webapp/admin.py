# Copyright (C) 2011 Philter Phactory Ltd.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE X
# CONSORTIUM BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# Except as contained in this notice, the name of Philter Phactory Ltd. shall
# not be used in advertising or otherwise to promote the sale, use or other
# dealings in this Software without prior written authorization from Philter
# Phactory Ltd..
#

from django.contrib import admin
import djangotoolbox.fields as toolbox
from django import forms
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.db import models
from django.contrib import messages
from django.utils.html import escape

try: from django.utils import simplejson as json
except ImportError: import json

import datetime

from models import *

try:
    from google.appengine.api.taskqueue import Task
except:
    from google.appengine.api.labs.taskqueue import Task


class ProstheticForm(ModelForm):
    class Meta:
        model = Prosthetic

    def __init__(self, *args, **kwargs):
        super(ProstheticForm, self).__init__(*args, **kwargs)

        # do at run time to avoid import import loop
        from introspection import prosthetic_class_lookup
        self.fields["classname"].choices = [ [ k, k ] for k in prosthetic_class_lookup ]
    

class ProstheticAdmin(admin.ModelAdmin):
    list_display = ( "name", "server", "classname", "show_on_homepage" )
    readonly_fields = ( "created", "blog_keyword", )
    form = ProstheticForm


class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ( "weavr_name", "prosthetic_desc", "oauth_key", "last_run", "last_success","enabled", "revoked", )
    actions = [ "enable_token", "disable_token", "run_token" ]

    list_filter = ["prosthetic", "enabled", "revoked", "last_success"]
    
    fieldsets = [
        ("Weavr", {
            "fields":[ "weavr_name", "weavr_url", ("prosthetic", "oauth_key", "oauth_secret"), ],
        }),

        ("State", {
            "fields":[ "revoked", "enabled", "data"],
        }),
        
        ("History", {
            "fields":["last_run", "last_success", "last_result", "pretty_historical_results"],
        }),
            
    ]
    readonly_fields = [ "oauth_key", "oauth_secret", "prosthetic", "weavr_url", "weavr_name", "pretty_historical_results", "last_success", "last_result" ]


    def changelist_view(self, request, extra_context=None):

        # don't apply changes if we're coming from an existing admin page, thus
        # allowing us to select 'ALL'
        if not request.META.get("QUERY_STRING", None):

            if not request.GET.has_key('revoked__exact'):
                q = request.GET.copy()
                q['revoked__exact'] = '0'
                request.GET = q
                request.META['QUERY_STRING'] = request.GET.urlencode()

            if not request.GET.has_key('enabled__exact'):
                q = request.GET.copy()
                q['enabled__exact'] = '1'
                request.GET = q
                request.META['QUERY_STRING'] = request.GET.urlencode()

        return super(AccessTokenAdmin,self).changelist_view(request, extra_context=extra_context)

    
    
    def pretty_historical_results(self, obj):
        if not obj.historical_results:
            return "No history"
        try:
            results = json.loads(obj.historical_results)
            def pretty_row(r):
                return "<b>%s:</b> %s"%(datetime.datetime.utcfromtimestamp(r[0]).strftime("%Y-%m-%d %H:%M"), escape(r[1]))
            return "<br>".join(map(pretty_row, results))
        except Exception, e:
            return "Error inflating results: %s (tried to inflate '%s')"%(e, obj.historical_results)
    pretty_historical_results.short_description = "History"
    pretty_historical_results.allow_tags = True
    
    def prosthetic_desc(self, obj):
        return unicode(obj.prosthetic)

    def disable_token(modeladmin, request, queryset):
        for q in queryset:
            q.enabled = False
            q.save()
    disable_token.short_description = "Disable Token"

    def enable_token(modeladmin, request, queryset):
        for q in queryset:
            q.enabled = True
            q.save()
    enable_token.short_description = "Enable Token"

    def run_token(modeladmin, request, queryset):
        for token in queryset:
            task = Task(url='/runner/run_task/', method='POST', params={'token': token.oauth_key, "force":"true"})
            task.add('default')
    run_token.short_description = "Force run of this token"


class RequestTokenAdmin(admin.ModelAdmin):
    list_display = ( "oauth_key", "prosthetic", "created", )



admin.site.register(Prosthetic, ProstheticAdmin)
admin.site.register(AccessToken, AccessTokenAdmin)
admin.site.register(RequestToken, RequestTokenAdmin)



def admin_action(request, key):
    token = get_object_or_404(AccessToken, id=key)

    if "enable" in request.POST:
        token.enabled = True
        token.save()
        messages.add_message(request, messages.SUCCESS, 'token enabled')
    
    if "disable" in request.POST:
        token.enabled = False
        token.save()
        messages.add_message(request, messages.SUCCESS, 'token disabled')
    
    if "force" in request.POST:
        task = Task(url='/runner/run_task/', method='POST', params={'token': token.oauth_key, "force":"true"})
        task.add('default')
        messages.add_message(request, messages.SUCCESS, 'run queued')
    
    return redirect("/admin/webapp/accesstoken/%s/"%key)

def view_blog(request, key):
    token = get_object_or_404(AccessToken, id=key)
    logging.info(token.blog_filter_url())
    return redirect(token.blog_filter_url())
    
