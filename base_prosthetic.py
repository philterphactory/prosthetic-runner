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

import datetime
import random
import re
import logging

try: from django.utils import simplejson as json
except ImportError: import json

class Prosthetic(object):
    """Base class for all prosthetics. Implements some defaults - prosthetics
    run once every 2 hours, and do nothing. They also have no post-oauth
    callback view, so anyone attaching a ptk will just be sent to the 'success'
    page.
    """

    def __init__(self, token):
        self.token = token
    
    def get(self, path, params = {}):
        return self.token.get_json( path, params )
    
    def post(self, path, params = {}):
        return self.token.post( path, params )
    
    # this will be called every run. return True if you did something
    def act(self, force=False):
        return False
    
    def post_oauth_callback(self):
        return None
        
    # run throttle
    @classmethod
    def time_between_runs(cls):
        # default to four hours
        return 3600 * 4
        


def persist_state(f):
    """If your ptk wants state, and you don't want to manage it yourself,
    use this as a decorator on your 'act' implementation. It'll store JSON in
    the 'data' property of the weavr token, presenting it as the 'state' property
    of the prosthetic instance.
    
        @persist_state
        def act(self, force):
            self.state["foo"] = "bar"
            return "persisted state!"

    """

    def wrap(self, *args, **argv):
        if self.token.data:
            self.state = json.loads(self.token.data)
        else:
            self.state = {}
        try:
            ret = f(self, *args, **argv)
        finally:
            self.token.data = json.dumps(self.state)
        # we can rely on the runner to save the token
        return ret
    return wrap

