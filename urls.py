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

import os
import logging

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

from webapp.introspection import prosthetics

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

raw_patterns = [

    (r'^accounts/', include('gaeauth.urls')),

    (r'^admin/accesstoken_action/(\d+)/$', 'webapp.admin.admin_action'),
    (r'^admin/accesstoken_blog/(\d+)/$', 'webapp.admin.view_blog'),
    (r'^admin/', include(admin.site.urls)),

    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout'),

    (r'^start_authorizing/(\w+)/$', "webapp.views.start_authorizing"),
    (r'^oauth_callback/$', "webapp.views.oauth_callback"),

    (r'^$', "webapp.views.home"),
    (r'^call/(.*?)/$', "webapp.views.call"),
    (r'^prosthetic/$', "webapp.views.prosthetics"),
    (r'^prosthetic/(\w+)/$', "webapp.views.prosthetic"),

    (r'^runner/run_cron/$', "webapp.views.cron"),
    (r'^runner/run_task/$', "webapp.views.task"),
    (r'^runner/ping_phloor/$', 'webapp.views.ping'),

    (r'^callback/$', "webapp.views.callback"),

]

# this is for backwards-compatibility. Pity.
if "dreamer" in settings.INSTALLED_APPS:
    raw_patterns.append((r'^dreamImage/(.*?)/$', "dreamer.views.dreamImage"))

for name in prosthetics:
    if os.path.exists(os.path.join(os.path.dirname(__file__), name, "urls.py")):
        __import__("%s.urls"%name)
        raw_patterns.append( ('^%s/'%name, include(name+".urls")) )

#logging.info("raw_patterns is %s"%(repr(raw_patterns)))

urlpatterns = patterns('', *raw_patterns)

