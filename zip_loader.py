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

"""
Wrapper for loading templates from zipfiles. Very crude. If a path in TEMPLATE_DIRS has '.zip'
in it, we'll look in there for the template. You can put file paths after the .zip and we'll append them
to the search path in the zipfile. Intended for pulling admin templates out of the django source zipfile
without having to unpack them.

    TEMPLATE_DIRS = (
        os.path.join(os.path.dirname(__file__), 'templates'),
        os.path.join(os.path.dirname(__file__), 'django-nonrel.zip/django/contrib/admin/templates"),
    )

    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'zip_loader.Loader',
    )

"""

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader
import re
import sys
import zipfile
import os

class Loader(BaseLoader):
    is_usable = True # because zipfile is core
    
    # cache open zipfiles - almost certainly worth doing, unless you have more zipfiles
    # in your template loader path than you have templates in zipfiles.
    zipfile_cache = {}
    def open_zipfile(self, filename):
        if filename in self.zipfile_cache and self.zipfile_cache[filename]:
            return self.zipfile_cache[filename]
        else:
            z = zipfile.ZipFile(filename)
            self.zipfile_cache[filename] = z
            return z


    def load_template_source(self, template_name, template_dirs=None):
        if not template_dirs:
            template_dirs = settings.TEMPLATE_DIRS
            
        tried = []

        for filepath in template_dirs:
            zipname = None
            zippath = None
            
            if re.search(r'\.zip$', filepath):
                zipname = filepath
                zippath = ""
            elif re.search(r'\.zip/', filepath):
                zipname = filepath.split(".zip/")[0] + ".zip"
                zippath = filepath.split(".zip/", 2)[1]
            
            if not zipname:
                continue
            
            try:
                z = self.open_zipfile(zipname)
                source = z.read(os.path.join(zippath, template_name))
                template_path = "%s:%s" % (filepath, template_name)
                return (source, template_path)
            except (IOError, KeyError):
                tried.append(filepath)

        if tried:
            error_msg = "Tried %s" % tried
        else:
            error_msg = "Your TEMPLATE_DIRS setting is empty. Change it to point to at least one template directory."
        raise TemplateDoesNotExist(error_msg)

    load_template_source.is_usable = True


_loader = Loader()

