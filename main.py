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

import sys,os
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'django-nonrel.zip'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'djangotoolbox.zip'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'html5lib.zip'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'bleach.zip'))

from djangoappengine.boot import setup_env
setup_env()


# We need to patch the manage.py command loader to look inside zipfiles,
# or it won't be able to find any of the important things like runserver
# or shell. By default, django assumes it can walk around in the filesystem,
# and that's not true any more.

# based on https://bitbucket.org/btoconnor/django-app-engine/src/78735e5f71cf/core/management/__init__.py
def find_commands(management_dir):
    """
    Given a path to a management directory, returns a list of all the command
    names that are available.

    This implementation also works when Django is loaded from a zip file.

    Returns an empty list if no commands are defined.
    """
    zip_marker = '.zip' + os.sep
    command_dir = os.path.join(management_dir, 'commands')
    if zip_marker not in command_dir:
        return original_find_commands(command_dir)

    import zipfile
    # Django is sourced from a zipfile, ask zip module for a list of files.
    filename, path = command_dir.split(zip_marker)
    zipinfo = zipfile.ZipFile(filename + '.zip')

    # The zipfile module returns paths in the format of the operating system
    # that created the zipfile! This may not match the path to the zipfile
    # itself. Convert operating system specific characters to '/'.
    path = path.replace('\\', '/')
    def _IsCmd(t):
        """Returns true if t matches the criteria for a command module."""
        t = t.replace('\\', '/')
        return t.startswith(path) and not os.path.basename(t).startswith('_') \
            and t.endswith('.py')

    return [os.path.basename(f)[:-3] for f in zipinfo.namelist() if _IsCmd(f)]

def original_find_commands(command_dir):
    """
    Given a path to a management directory, returns a list of all the command
    names that are available.

    Returns an empty list if no commands are defined.
    """
    try:
        return [f[:-3] for f in os.listdir(command_dir)
                if not f.startswith('_') and f.endswith('.py')]
    except OSError:
        return []


def find_management_module(app_name):
    """
    Determines the path to the management module for the given app_name,
    without actually importing the application or the management module.

    Raises ImportError if the management module cannot be found for any reason.
    """
    parts = app_name.split('.')
    parts.append('management')
    parts.reverse()
    part = parts.pop()
    path = None

    # When using manage.py, the project module is added to the path,
    # loaded, then removed from the path. This means that
    # testproject.testprojectmodels can be loaded in future, even if
    # testproject isn't in the path. When looking for the management
    # module, we need look for the case where the project name is part
    # of the app_name but the project directory itself isn't on the path.
    return os.path.dirname(__import__(app_name + '.management',
                                      {}, {}, ['']).__file__)



# monkey-patch our new management-command-loader into django-core
from djangoappengine.utils import have_appserver
if not have_appserver:
    from django.core import management
    management.find_commands = find_commands
    management.find_management_module = find_management_module



if __name__ == '__main__':
    from djangoappengine.main.main import main
    main()
