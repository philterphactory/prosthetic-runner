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
from django import template
register = template.Library()

from django.utils.safestring import mark_safe

import bleach

bleach.ALLOWED_TAGS += ['p','img']
bleach.ALLOWED_ATTRIBUTES["img"] = ["src"]

@register.filter
def bleach_html(html):
    """ 
    Convert raw, unsafe, "users wrote this" HTML into nice safe displayable
    HTML.
    """ 
    
    clean = bleach.clean(html).strip()
    
    # if the source doesn't include <p> tags, enforce them.
    if not re.search(r'^<p>', clean):
        clean = "<p>%s</p>"%clean
    
    # now the template can treat this string as HTML safely
    return mark_safe(clean)


