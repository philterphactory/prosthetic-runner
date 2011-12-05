# Initialize App Engine and import the default settings (DB backend, etc.).
# If you want to use a different backend you have to remove all occurences
# of "djangoappengine" from this file.
from djangoappengine.settings_base import *
import logging
import os
import re

TEMPLATE_DEBUG = True

SECRET_KEY = 'o448734958734958374598347593'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'djangotoolbox',
    # djangoappengine should come last, so it can override a few manage.py commands
    'djangoappengine',
    
    # the runner framework
    'webapp',
    
    # the errormon helper
    'errormon',
    
    # prosthetics are auto-added to this list
]

MIDDLEWARE_CLASSES = (
    #'google.appengine.ext.appstats.recording.AppStatsDjangoMiddleware',
    'errormon.middleware.ExceptionStoreMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
)

ADMIN_MEDIA_PREFIX = '/django-nonrel/django/contrib/admin/media/'

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
    os.path.join(os.path.dirname(__file__), 'django-nonrel.zip', "django/contrib/admin/templates"),
)

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
    'zip_loader.Loader',
)


ROOT_URLCONF = 'urls'

AUTHENTICATION_BACKENDS = ('webapp.auth.HackyGoogleAccountBackend',)
LOGIN_REDIRECT_URL = '/admin/'

INSTANCE_NAME = re.sub(r'^s~','', os.environ.get("APPLICATION_ID", "localhost"))
try:
  APPENGINE_DEV = os.environ['SERVER_SOFTWARE'].startswith('Dev')
except:
  APPENGINE_DEV = False

DEBUG = False
LOCAL_SERVER = "%s.appspot.com" % INSTANCE_NAME

if APPENGINE_DEV:
    LOCAL_SERVER = "localhost:8001"
    DEBUG=True
    MIDDLEWARE_CLASSES += ('errormon.middleware.IdeDebugMiddleware',)

elif INSTANCE_NAME == 'weavrdreamr':
    LOCAL_SERVER = 'www.weavrdreamr.com'

elif INSTANCE_NAME == 'recipeer-live':
    LOCAL_SERVER = 'recipeer.ptk.weavrs.com'

elif INSTANCE_NAME == 'sloganeer-live':
    LOCAL_SERVER = 'sloganeer.ptk.weavrs.com'

elif INSTANCE_NAME == 'whistlingweavrs':
    LOCAL_SERVER = 'www.weavrwhistlr.com'

elif INSTANCE_NAME == 'emotional-live':
    LOCAL_SERVER = 'www.wovenemotion.com'

elif INSTANCE_NAME == 'prosthetic-dev':
    DEBUG=True



# Activate django-dbindexer if available
try:
    import dbindexer
    DATABASES['native'] = DATABASES['default']
    DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}
    INSTALLED_APPS += ('dbindexer',)
    DBINDEXER_SITECONF = 'dbindexes'
    MIDDLEWARE_CLASSES = ('dbindexer.middleware.DBIndexerMiddleware',) + \
                         MIDDLEWARE_CLASSES
except ImportError:
    pass

# look for prosthetic folders
root = os.path.dirname(__file__)
for folder in os.listdir(root):
    if os.path.isdir(os.path.join(root, folder)): # dereferences symlinks
        if os.path.isfile(os.path.join(root, folder, "prosthetic.py")):
            if not folder in INSTALLED_APPS:
                #logging.info("installing prosthetic %s"%folder);
                INSTALLED_APPS.append(folder)

# customize session so not to clash with other django instances
SESSION_COOKIE_NAME = 'ptksession'
