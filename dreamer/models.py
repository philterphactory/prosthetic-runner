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

import random
import urllib
import logging

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import images
from google.appengine.api import urlfetch

from webapp.models import AccessToken

# cache generated images in the datastore.
class ImageCache(db.Model):
    url = db.StringProperty()
    image = db.BlobProperty()

    
    # fetches images from the internet, manipulates then, and then caches in the datastore.
    # TODO - once you can programatically write to the blobstore, we should do that, because
    # GAE will let you serve binaries directly from the blobstore without having to activate
    # a handler.
    @classmethod
    def generate_image(cls, url):
        image_data = urlfetch.Fetch(url).content
        
        image = cls.weave(image_data)
        if not image:
            return None

        blob = db.Blob(image)
        cache = cls(url=url, image=blob)
        cache.save()
        return cache

    
    @classmethod
    def weave(cls, image_data):
        
        # where in the image to crop the box. numbers are relative to image
        # make sure max width + crop width can never be > 1 !! Likewise height.
        left = 0.0 + random.uniform(0,0.4)
        top = 0.4 + random.uniform(0,0.2)
        crop_width = 0.1 + random.uniform(0,0.3) # width of the box, as a proportion of the image width

        # target tile width and height. Image will be twice as wide/high
        target_width = 500/2
        target_height = 320/2

        # the box wants to be in the aspect ratio of the output file.
        try:
            image = images.Image(image_data)
            ratio = float(image.width) / image.height
        except images.NotImageError, e:
            logging.error("Can't parse image: %s"%e)
            return None # not a lot we can do here.

        logging.info("width is %s height is %s Ratio is %s"%(image.width, image.height, ratio))
        crop_height = ( crop_width * ratio ) * (float(target_height)/target_width)

        # don't fall outside of the bounding box. Really shouldn't happen, and it
        # messes with the nice distribution of the boxes, but it's better than dying.
        if crop_height + top > 1:
            top = 1 - crop_height
        if crop_width + left > 1:
            left = 1 - crop_width

        image.crop(left, top, left + crop_width, top + crop_height)

        tile = image.execute_transforms(images.JPEG)

        tile_image = images.Image(tile) # need to do this to get width/height. Sigh.
        logging.info("image is %s by %s"%(tile_image.width, tile_image.height))

        # issue here - the crop function might not produce an image of the
        # exact required aspect ratio, so when we resize to the desired tile size
        # here, we dont get an image of the exact right size. To avoid hairline
        # cracks, make sure we composite before we resize.
        w = tile_image.width - 1
        h = tile_image.height - 1
        one = images.composite([
            (tile, 0, 0, 1.0, images.TOP_LEFT),
            (images.horizontal_flip(tile), w, 0, 1.0, images.TOP_LEFT),
            (images.vertical_flip(tile), 0, h, 1.0, images.TOP_LEFT),
            (images.horizontal_flip(images.vertical_flip(tile)), w, h, 1.0, images.TOP_LEFT),
        ], w * 2, h * 2, output_encoding=images.JPEG)

        return images.resize(one, target_width * 2, target_height * 2, output_encoding=images.JPEG)

