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

# ----
# A simple prosthetic wrapper to expose the weavrs api methods into a js context
# to facilitate presentation and visualization of weavrs data 
# and activity outside of their blogs.
# ----
import logging

from django.conf import settings
from django.http import HttpResponse, Http404
from django.template.context import RequestContext
from django.shortcuts import render, render_to_response, get_object_or_404

from jswrapper.prosthetic import JsWrapper
from webapp.models import AccessToken, Prosthetic

try: from django.utils import simplejson as json
except ImportError: import json


def getAccessTokenFor(weavr_name):
    """Helper function to get the access token associated with the passed
       weavr_name and throw a 404 error if token not found
    """
    try:
        access_tokens = AccessToken.objects\
               .filter(weavr_name=weavr_name,revoked=False,enabled=True)
    except IndexError:
        logging.error("access token not found for weavr %s" % weavr_name)
        raise Http404
    access_token = False
    for token in access_tokens:
        if token.prosthetic.name == 'jswrapper':
            access_token = token
    if not access_token:
        logging.error("jswrapper access token not found for weavr %s" % weavr_name)
        raise Http404
    return access_token


def dictFromQuerydict(qdict):
    params = {}
    if not qdict:
        return params
    params.update(qdict)
    logging.info(params)
    for k in params.keys():
        if (hasattr(params[k], "__iter__")):
            if not params[k][0]:
                del params[k]
            else:
                params[k] = params[k][0]
        else:
            if not params[k]:
                del params[k]
    logging.info(params)
    return params


def apiProxy(request, weavr_name, method):
    """Simple api wrapper that grabs the access token for the weavr_name
       instantiates an instance of the jswrapper prosthetic and then passes 
       the api method called onto the get method in the prosthetic base class
       and returns the results in an http response as json
    """
    access_token = getAccessTokenFor(weavr_name)
    prosthetic_api_wrapper = JsWrapper(access_token)
    logging.info(request.REQUEST)
    params = dictFromQuerydict(request.REQUEST)
    if method == 'post-write':
        json = prosthetic_api_wrapper.post("/1/weavr/post/", params)
    else:
        json = prosthetic_api_wrapper.get("/1/weavr/%s/" % method, params)
    return HttpResponse(content=simplejson.dumps(json), mimetype="application/json")


def generic_js_view(request, view_name, weavr_name):
    access_token = getAccessTokenFor(weavr_name)
    prosthetic = access_token.prosthetic
    title = getattr(prosthetic, "view_title", "Untitled Prosthetic")
    template = getattr(prosthetic, "view_template", "jswrapper/missing_template.html")

     # TODO for james: remove these backwards compatibility hacks
    if view_name == "demo":
        title    = "Javascript Wrapper for the Weavrs API"
        template = "jswrapper/index.html"
    elif view_name == "walk":
        title    = "Weavrs Walk"
        template = "jswrapper/walk.html"
    elif view_name == "waevrsthetic":
        title    = "Waevrsthetic"
        template = "jswrapper/waevrsthetic.html"
    elif view_name == "feltromata":
        title    = "Feltromata"
        template = "jswrapper/feltromata.html"
    # end TODO

    HUB_URL = 'http://%s/' % prosthetic.server
    DEBUG = True #settings.DEBUG
    return render_to_response(template,
           locals(), context_instance=RequestContext(request))
