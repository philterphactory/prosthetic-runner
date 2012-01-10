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

from django.http import HttpResponse, HttpResponseNotFound
from google.appengine.api.taskqueue.taskqueue import Task
from google.appengine.ext.deferred import deferred
from errormon.views import admin_required

from models import *


# serves cached images from the datastore.
def dreamImage(request, key):
    image = db.get(key)
    if image and image.image:
        logging.info("got image %s"%image)
        return HttpResponse(image.image, mimetype="image/jpeg")
    else:
        return HttpResponseNotFound()


# generates an image on demand - useful for testing, not production use.
def dreamTest(request):
    url = request.REQUEST.get("url")
    image_data = urlfetch.Fetch(url).content
    image = ImageCache.weave(image_data)
    return HttpResponse(image, mimetype="image/jpeg")

# secure using GAE @admin_required
def fixImageCaches(request):
    queueFixImageCaches(0)
    return HttpResponse('QUEUED')

def queueFixImageCaches(offset, countdown=0):
    task = Task(url="/dreamer/admin/run-fix-image-caches/%d" % offset, method="POST", countdown=countdown)
    task.add('default')

# secure using GAE @admin_required
def runFixImageCaches(request, offset):
    offset = int(offset)
    limit = 50
    query = ImageCache.all(keys_only=True).fetch(limit + 1, offset)
    results = list(query)
    if len(results) > limit:
        results.pop()
        continue_at = offset + limit
    else:
        continue_at = None
    i = 0
    for result in results:
        i += 1
        countdown = max(0, offset + (i / 2))
        task = Task(url="/dreamer/admin/fix-image/%s" % result.id_or_name(), method="POST", countdown=countdown)
        task.add('default')
    if continue_at:
        queueFixImageCaches(continue_at, countdown=max(10, limit/2))
    return HttpResponse('OK')

# secure using GAE @admin_required
def runFixImageCache(request, imageId):
    cache = None
    try:
        imageIdInt = int(imageId)
    except ValueError:
        pass
    else:
        cache = ImageCache.get_by_id(imageIdInt)
    if cache is None:
        cache = ImageCache.get_by_key_name(imageId)

    if cache is None:
        logging.warning(u"Cannot find image cache %s to fix" % imageId)
        return HttpResponse()
    
    image_data = urlfetch.Fetch(cache.url).content
    
    image = ImageCache.weave(image_data)
    if not image:
        return HttpResponse()

    blob = db.Blob(image)
    cache.image = blob
    cache.save()
    logging.info(u"Fixed image %s" % imageId)
    return HttpResponse()
