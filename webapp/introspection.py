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
import re
import logging
import base_prosthetic

from django.conf import settings
import webapp.models

prosthetics = []

# on startup, introspect the loaded apps and look for prosthetics
for app in settings.INSTALLED_APPS:
    ptk_file = os.path.join(os.path.dirname(__file__), "..", app, "prosthetic.py")
    if os.path.exists(ptk_file):
        __import__("%s.%s"%(app,"prosthetic"))
        prosthetics.append(app)

# we've imported all the files, so now
prosthetic_classes = base_prosthetic.Prosthetic.__subclasses__()

#logging.info("Found prosthetics %r"%prosthetic_classes)

prosthetic_class_lookup = dict([(p.__module__+"."+p.__name__, p) for p in prosthetic_classes])

def ptk_class_by_name(name):
    for p in prosthetic_classes:
        if p.__module__ + "." + p.__name__ == name:
            return p
    return None

