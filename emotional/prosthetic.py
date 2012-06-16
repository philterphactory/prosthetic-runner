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

from base_prosthetic import Prosthetic
import logging

class Emotional(Prosthetic):
    """A trivial demo prosthetic that just blogs the weavr's current and last
    emotional state on every run."""

    def act(self, force=False):
        state = self.get("/1/weavr/state/")
        if not state["awake"] and not force:
            logging.info("weavr is sleeping. not emotional.")
            return "weavr is asleep - refusing to be emotional"

        emotion = state["emotion"]
        
        # store previous emotion in token data object.
        previous_emotion = self.token.data
        
        if not previous_emotion:
            self.token.data = emotion
            return "this is my first run. Storing current emotion '%s' and finishing"%emotion
        

        if emotion != previous_emotion:
            message = "I was feeling %s, but now I'm %s" % (previous_emotion, emotion)
            # The emotion changed, so save it
            self.token.data = emotion
        else:
            message = "I am still feeling " +  emotion

        logging.info("sending new status: %s"%message)

        self.post("/1/weavr/post/", {
            "category":"status",
            "status":message,
            "keywords":emotion,
        })
        
        return message



