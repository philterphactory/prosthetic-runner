import datetime

try:
    import json
except ImportError:
    try:
        from django.utils import simplejson as json
    except ImportError:
        import simplejson as json
import oauth2 as oauth
from bottle import abort

import settings
import models


class WeavrsClient(object):
    def __init__(self, weavrs_instance, weavr, api_version='1'):
        if isinstance(weavrs_instance, basestring):
            weavrs_instance = models.WeavrsInstance.get_by_key_name_or_abort(key_name=weavrs_instance)
        if isinstance(weavr, basestring):
            weavr = get_weavr_or_abort(weavrs_instance, weavr)
        if weavr.oauth_revoked:
            abort(500, u"Cannot use weavr %s because it doesn't have valid OAuth credentials" % weavr.name)
        self.weavrs_instance = weavrs_instance
        self.weavr = weavr
        self.consumer = oauth.Consumer(weavrs_instance.consumer_key, weavrs_instance.consumer_secret)
        self.access_token = oauth.Token(self.weavr.oauth_key, self.weavr.oauth_secret)
        self.client = oauth.Client(self.consumer, self.access_token)
    
    def get_json(self, action):
        api_url = self.weavrs_instance.get_api_url(action)
        
        resp, content = self.client.request(api_url, 'GET')
        status = resp.status
        if status == 401:
            self.weavr.revoked = datetime.datetime.now()
            self.weavr.save()
            abort(400, u"OAuth credentials for weavr %s have been revoked" % weavr.name)
        elif status >= 500:
            abort(503, u"Could not access weavrs instance at %s, status %d" % (
                    api_url, status))
        elif status >= 400:
            abort(500, u"Could not access weavrs instance at %s, status %d" % (
                    api_url, status))
        elif status >= 300:
            abort(500, u"Could not access weavrs instance at %s, status %d" % (
                    api_url, status))
        return json.loads(content)
    
    def get_weavr_configuration(self):
        return self.get_json('weavr/configuration')
