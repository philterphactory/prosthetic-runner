# Copyright (C) 2012 Philter Phactory Ltd.
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
# Phactory Ltd.

from django.db import models
from webapp.models import AccessToken

class Run( models.Model ):
    weavr_token = models.ForeignKey(AccessToken, related_name="state_weavr")
    last_replied_id = models.CharField( max_length=20, default='1' ) # twitter API doesn't like 0   
    last_run = models.DateTimeField( auto_now_add=True )
    last_post = models.CharField( max_length=200, blank=True )
    last_post_url = models.CharField( max_length=200, blank=True )
    last_post_date = models.DateTimeField( auto_now_add=True, blank=True )
    blog_url = models.CharField( max_length=200, blank=True )
    weavr_name = models.CharField( max_length=200, blank=True )

class ApplicationConfig( models.Model ):
    twitter_api_url = models.CharField( max_length=500,
                                        default="api.twitter.com")
    twitter_api_root = models.CharField( max_length=500,
                                         null=True, blank=True,
                                         default=None)

def current_app_config():
    """Get the current application configuration"""
    return ApplicationConfig.objects.all()[0]

def current_twitter_api_url():
    return current_app_config().twitter_api_url

def current_twitter_api_root():
    return current_app_config().twitter_api_root
