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
import re
import logging
import time
import random

from django.core.urlresolvers import reverse
from django.conf import settings

from base_prosthetic import Prosthetic, persist_state

from models import ImageCache

# the prosthetic itself.
class Dreamer(Prosthetic):

    # run throttle
    @classmethod
    def time_between_runs(cls):
        # run every two hours. Dreams don't happen every two hours, though.
        return 3600 * 2

    # called from the task queue, once an hour (or whatever)
    @persist_state
    def act(self, force=False):

        state = self.get("/1/weavr/state/")
        if state["awake"] and not force:
            logging.info("weavr is awake. not dreaming.")
            return "weavr is awake - refusing to dream"

        # don't dream all the time.
        if random.random() > 0.5:
            return "I don't feel like dreaming right now"

        # find all the image posts that I _didn't_ write.
        since = datetime.datetime.utcnow() - datetime.timedelta(days = 2)
        posts = self.get("/1/weavr/post/", { "category":"image", "after":since.strftime("%Y-%m-%dT%H:%M:%SZ") })["posts"]
        images = filter(lambda p: (p["category"] == 'image') and (not p["posted_by_calling_prosthetic"]), posts)
        logging.info("got images " + repr(images))
        
        if not images:
            logging.info("no recent images")
            return "No recent images"

        # for now, just pick one at random
        image_post = random.choice(images)
        
        # pick 2 random keywords from it
        keywords = random.sample(image_post["keywords"].split(), 2)
        
        # construct path to image served through the local prosthetic server.
        image_source = image_post["image_url"]
        
        # this isn't safe - not all images _have_ these sizes.
        #if re.search(r'^http://farm\d+\.static\.flickr\.com/', image_source):
        #    image_source = re.sub(r'([\w\d]{5})\.jpg$',r'\1_b.jpg', image_source)
            
        logging.info("dreaming about %s"%image_source)

        cache = ImageCache.generate_image(image_source)
        if not cache:
            raise Exception("failed to generate an image")

        image_url = "http://%s/dreamImage/%s/"%( settings.LOCAL_SERVER, cache.key())
        image_src = image_post["blog_post_short_url"] # source_url

        # allow for maybe one keyword.
        def link_keyword(k):
            return """<a href="/filter/%s">#%s</a>"""%(k,k)
        and_string = " and ".join(map(link_keyword, keywords))

        emotion = state["emotion"]

        title = """I'm dreaming something about %s"""%( re.sub(r'<.*?>','',and_string) )
        html = """
        <p><a href="%(image_src)s"><img src="%(image_url)s"></a></p>
        
        <p>I'm dreaming. Something about %(and_string)s, not sure, but I'm feeling <a href="/filter/%(emotion)s">%(emotion)s</a>.</p>
        
        """%locals()
        
        post = self.post("/1/weavr/post/", {
            "category":"article",
            "title":title,
            "body":html,
            "keywords":" ".join(keywords + ["dream"]),
        })
        
        self.state["last_post"] = time.time()
        self.state["last_post_id"] = post["post_id"]
        if not "posts" in self.state:
            self.state["posts"] = []
        self.state["posts"].append( post["post_id"] )
        
        if len(self.state["posts"]) > 30:
            self.state["posts"][-20:]

        return "posted about %s: %s"%( and_string, repr(post) )







