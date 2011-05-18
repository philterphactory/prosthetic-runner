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

import httplib
import logging
import oauth.oauth as oauth
import re
import urlparse
import cgi

# python 2.6
try: import simplejson as json
except ImportError: import json

################################################################################
# API OAuth Access class
################################################################################

class OAuthForbiddenException(Exception):
    pass

class OAuthUnauthorizedException(Exception):
    pass

class OAuthServerException(Exception):
    pass
    
class OAuthWrangler(object):
    """OAuth registration and resource access support"""

    def __init__(self, api_server, consumer_key, consumer_secret, debug = 100):
        """Create the objects we need to connect to an OAuth server"""
        self.api_server = api_server
        oauth_server_path = 'http://%s/oauth' % api_server
        self.request_token_url = oauth_server_path + '/request_token/'
        self.access_token_url = oauth_server_path + '/access_token/'
        self.authorization_url = oauth_server_path + '/authorize/'

        self.connection = httplib.HTTPConnection(api_server)
        self.connection.set_debuglevel(debug)
        self.consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self.signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
        self.signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
    
    def check_response(self, connection):
        response = connection.getresponse()
        body = response.read()
        logging.info("response status is %s"%response.status)

        if re.search(r'Invalid access token', body) and re.search(r"Status: 401", body):
            # annoying server bug is returning bad error responses
            raise OAuthUnauthorizedException()

        if re.search(r'Invalid access token', body) and re.search(r"Status: 403", body):
            # annoying server bug is returning bad error responses
            raise OAuthForbiddenException()

        if response.status >= 200 and response.status < 300:
            return body
        if response.status == 401:
            raise OAuthUnauthorizedException()
        if response.status == 403:
            raise OAuthForbiddenException()

        logging.error("unexpected server response %d: %s"%(response.status,body))
        raise OAuthServerException(body)

    def get_request_token(self):
        """Get the initial request token we can exchange for an access token"""
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(\
            self.consumer, http_url=self.request_token_url)
        oauth_request.sign_request(self.signature_method_plaintext, self.consumer, None)
        self.connection.request(oauth_request.http_method, self.request_token_url,
                                headers=oauth_request.to_header())
        
        body = self.check_response(self.connection)
        # Because why should read return just the body?
        if '\n\n' in body:
            body = body.split('\n\n')[1]
        return oauth.OAuthToken.from_string(body)



    def authorize_request_token_url(self, token, callback_url=None):
        """Get the url to use to authorize the token"""
        oauth_request = oauth.OAuthRequest.from_token_and_callback(\
            token=token, http_url=self.authorization_url, callback=callback_url)
        return oauth_request.to_url()

    def get_access_token(self, token, verifier):
        """Exchange the request token for an access token"""
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(\
            self.consumer, token=token, verifier=verifier, 
            http_url=self.access_token_url)
        oauth_request.sign_request(self.signature_method_plaintext, self.consumer, token)
        self.connection.request(oauth_request.http_method, self.access_token_url,
                                headers=oauth_request.to_header())

        return oauth.OAuthToken.from_string(self.check_response(self.connection))

    def get_resource(self, token, resource_url, paramdict = {}):
        """GET an OAuth resource"""
        if resource_url[0] == "/":
            # absolute path on server
            resource_url = "http://%s/api%s"%(self.api_server, resource_url)
        
        # pull query pparams off the URI
        logging.info("params are %r"%paramdict)
        query = cgi.parse_qs(urlparse.urlsplit(resource_url).query)
        for k in query:
            if not k in paramdict:
                paramdict[k] = query[k][0]
        logging.info("params are %r (added %r)"%(paramdict, query))
        
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(\
            self.consumer, token=token, http_method='GET',
            http_url=resource_url, parameters=paramdict)
        oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, token)
        self.connection.request(oauth_request.http_method, oauth_request.to_url())
        return self.check_response(self.connection)
    
    # convenience wrapper, parses response as JSON.
    def get_json(self, token, resource_url, paramdict = {}):
        response = self.get_resource(token, resource_url, paramdict)
        #logging.info("got response " + response)
        try:
            return json.loads(response)
        except ValueError:
            logging.warn("Can't decode response: %s"%response)
            raise

    def post_resource(self, token, resource_url, paramdict):
        """POST an OAuth resource"""
        if resource_url[0] == "/":
            # absolute path on server
            resource_url = "http://%s/api%s"%(self.api_server, resource_url)
        utf8dict = {}
        for param in paramdict:
            utf8dict[param.encode("utf8")] = paramdict[param].encode("utf8")
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(\
            self.consumer, token=token, http_method='POST',
            http_url=resource_url, parameters=utf8dict)
        oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, token)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.connection.request(oauth_request.http_method, resource_url,
                                body=oauth_request.to_postdata(),
                                headers=headers)
        return self.check_response(self.connection)

    # convenience wrapper, parses response as JSON.
    def post_json(self, token, resource_url, paramdict):
        response = self.post_resource(token, resource_url, paramdict)
        try:
            return json.loads(response)
        except ValueError:
            logging.warn("Can't decode response: %s"%response)
            raise

