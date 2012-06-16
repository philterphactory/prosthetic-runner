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

import re
import sys, traceback, os
import time
import logging
from datetime import datetime
   
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.utils.http import urlquote_plus, urlencode
   
from google.appengine.api import urlfetch
   
import oauth.oauth as oauth
   
try: from django.utils import simplejson as json
except ImportError: import json
   
from client import OAuthForbiddenException

   
try:
    from google.appengine.api.taskqueue import Task
except:
    from google.appengine.api.labs.taskqueue import Task
   
from models import AccessToken, RequestToken, Prosthetic, ProstheticException
   
from introspection import prosthetic_class_lookup
   
   
def render_error(request, error):
    return render_to_response("error.html", locals(),
        context_instance=RequestContext(request))
   
   
def home(request):
    # pick an appropriate prosthetic for the homepage
    try:
        single_prosthetic = Prosthetic.objects.filter(show_on_homepage = True)[0]
        # now just pretend we're displaying that prosthetic
        return prosthetic(request, single_prosthetic.id, prosthetic=single_prosthetic)
    except IndexError:
        # nothing flagged as show_on_homepage. Try showing all of them
        try:
            prosthetics = Prosthetic.objects.all()
            return render_to_response("home.html", locals(),
                                      context_instance=RequestContext(request))
        except IndexError:
            # no prosthetics at all.
            raise Http404
      
def prosthetics(request):
    prosthetics = Prosthetic.objects.all()
     
    missing = []
    for name in prosthetic_class_lookup.keys():
        if not name in [ p.classname for p in prosthetics ]:
            logging.info("prosthetic %s is not represented"%name)
            doc = getattr(prosthetic_class_lookup[name], "__doc__")
            missing.append({ "classname":name, "name":name.split(".")[-1], "doc":doc })
   
    return render_to_response("prosthetics.html", locals(),
        context_instance=RequestContext(request))
   
  
def prosthetic(request, key, prosthetic=None):
    # prosthetic var might be set because we're passing it from the
    # home() function, and I don't want to look it up twice.
    if not prosthetic:
        prosthetic = get_object_or_404(Prosthetic, id=key)
    # show or hide user login
    hide_usernav = True
    title = "Weavrs Prosthetic > %s" % prosthetic.name
    # show or hide list of associated weavrs
    show_associated = False
    return render_to_response("prosthetic.html", locals(),
                              context_instance=RequestContext(request))


@login_required
def call(request, token_id):
    token = get_object_or_404(AccessToken, id=token_id)
    method = request.REQUEST.get("m", None)
    logging.info("method is %s"%method)
    
    if method:
        try:
            result = json.dumps( token.get_json(method, {}), indent = 4 )
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            result_error = unicode(exc_value) + "\n" + "".join(traceback.format_tb(exc_traceback))

    return render_to_response("call.html", locals(),
                              context_instance=RequestContext(request))

@csrf_exempt
def callback(request):
    logging.info("callback request incoming! (%r)"%request.POST)
    return HttpResponse()

# OAuth control
   
def start_authorizing(request, key):
    """Get the initial access token and send the user to authorize it"""
    prosthetic = get_object_or_404(Prosthetic, id=key)
    wrangler = prosthetic.wrangler()
   
    try:
        token = wrangler.get_request_token()
        # Save the token ready for the callback
        try:
            token = RequestToken.objects.get(oauth_key=token.key)
            logging.error("request token for key already exists!")
            token.delete()
        except RequestToken.DoesNotExist:
            pass
   
        request_token = RequestToken(oauth_key=token.key, oauth_secret=token.secret, prosthetic=prosthetic)
        request_token.save()
   
        callback_url = "http://%s/oauth_callback/"%settings.LOCAL_SERVER
   
        start = wrangler.authorize_request_token_url(token, callback_url)
        return redirect(start)
    except urlfetch.DownloadError, e:
        return render_error(request, "Can't connect to API server: %s"%(e))
   
   
   
#@login_required
def oauth_callback(request):
    """Accept the authorization from the server and store the data we use to communicate with the Weavr"""
    token = request.REQUEST.get('oauth_token')
    verifier = request.REQUEST.get('oauth_verifier')
    confirmed = request.REQUEST.get('oauth_callback_confirmed')
    
   
    # Make sure we have the required parameters
    if (not verifier) or (not token):
        return render_error("missing params")
    if not confirmed:
        return render_error("connection wasn't confirmed")
   
    # Get the token and store the verifier
    request_token = get_object_or_404(RequestToken, oauth_key=token)
    if not request_token:
        return render_error("invalid request token")
        
    prosthetic = request_token.prosthetic
    cls = prosthetic.get_class()
    if not cls:
        raise Exception("Can't get class for prosthtic")
      
    # verify the token and create a local object
    verified_token = oauth.OAuthToken(request_token.oauth_key, request_token.oauth_secret)
    access_token = request_token.prosthetic.wrangler().get_access_token(verified_token, verifier)
    access_object = AccessToken(oauth_key=access_token.key, oauth_secret=access_token.secret, prosthetic=request_token.prosthetic,enabled=True)
   
    # make an API call with the token before we save it.
    configuration = access_object.get_json("/1/weavr/configuration")
    access_object.weavr_name = configuration['name']
    access_object.weavr_url = configuration['blog']
    if "post_keyword" in configuration:
        access_object.prosthetic.blog_keyword = configuration['post_keyword']
    
    # everything worked. Save access token
    access_object.save()
    request_token.delete() # don't need this any more
    
    # if the ptk wants to do something at this point, it is able to.
    ptk = cls(access_object)
    post_oauth_callback = ptk.post_oauth_callback()
    if post_oauth_callback:
        return post_oauth_callback
    
    # show or hide user login
    hide_usernav = True
    return render_to_response("success.html", locals(),
        context_instance=RequestContext(request))
  
  
 
def queue_token_run(token):
    cls = token.prosthetic.classname
    logging.info("Queueing run task for token %s for %s on %s"%( token.oauth_key, token.weavr_name, cls ))
    task = Task(url='/runner/run_task/', method='POST', params={'token': token.oauth_key})
    task.add('default')
   
def cron(request):
    # preload prosthetics
    prosthetics = dict([ [p.id, p.get_class()] for p in Prosthetic.objects.all().iterator() ])
    
    # queue run tasks for prosthetics that 'should_act'
    for token in AccessToken.objects.filter(enabled=True,revoked=False):
        prosthetic_class = prosthetics[ token.prosthetic_id ]
        
        if not prosthetic_class:
            logging.info("not running token %s: can't load prosthetic class"%token.oauth_key)
            continue

        if token.last_run:
            time_since_last_run = datetime.now() - token.last_run
            time_since_last_run_seconds = 86400 * time_since_last_run.days + time_since_last_run.seconds
            if time_since_last_run_seconds < prosthetic_class.time_between_runs():
                logging.info("not running %s on %s: only %d seconds since last run - need %d"%(prosthetic_class.__name__, token.weavr_name, time_since_last_run_seconds, prosthetic_class.time_between_runs()))
                continue

        queue_token_run(token)

    return HttpResponse("queued all links")
   
   
def task(request):
    # key of the token to run
    key = request.POST.get("token")
    token = get_object_or_404(AccessToken, oauth_key=key)
     
    # set this to force a run even if the last run was recent
    force = request.POST.get("force", None) and True or False
  
    logging.info("running token %s"%token)
  
    cls = token.prosthetic.get_class()
  
    try:
        token.last_result = cls(token).act(force)
        token.last_success = True
    except Exception:
        token.last_success = False
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.warn("Exception: %s / %s"%( exc_type, exc_value ))
        logging.warn("".join(traceback.format_tb(exc_traceback)))
        token.last_result = "Exception: %s / %s"%( exc_type, exc_value )
  
    if token.historical_results:
        history = json.loads(token.historical_results)
    else:
        history = []
    history.insert(0, ( time.time(), token.last_result ))
    if len(history) > 20:
        history = history[0:20]
    token.historical_results = json.dumps(history)
  
    token.last_run = datetime.now()
    token.save()
  
    return HttpResponse(token.last_result, content_type = "text/plain")


def ping(request):
    server = "http://phloor.weavrs.com/ping/"
    if settings.APPENGINE_DEV:
        logging.info("pinging local dev environment")
        server = "http://localhost:8002/ping/"

    instance_name = os.environ.get("APPLICATION_ID", "localhost")
    
    try:
        from deploy_data import data
    except ImportError:
        data = dict(revision="",shipped="")
    
    logging.info("ship data is %s"%repr(data))

    payload=dict(
        name=instance_name,
        type="prosthetic-runner",
        url="http://%s"%settings.LOCAL_SERVER,
        deployed_at=data["shipped"],
        revision=data["revision"],
        version=data["version"],
    )
    try:
        urlfetch.fetch(server, deadline=1000, method="POST", payload=urlencode(payload))
    except Exception, e:
        logging.warn("can't ping phloor: %s"%e)

    return HttpResponse()
    