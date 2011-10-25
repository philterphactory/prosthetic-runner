## Prerequisites

* Google App Engine SDK installed


## Running the prosthetic server locally

* copy app.yaml.local.template to app.yaml.local and edit to include an application name. (can be anything for local development)
* Create a super-user with the following commands in the python console:

```python    
    from django.contrib.auth.models import User
    su = User.objects.create_user('admin', 'admin@localhost', 'password') 
    su.is_staff = True
    su.is_superuser = True 
    su.save()
```

* run "python manage.py runserver" to start the prosthetic server on http://localhost:8000/


## Running the prosthetic server remotely

* register a google app engine domain (http://appengine.google.com/)
* copy app.yaml.local.template to app.yaml.local and edit to include the name of your registered domain
* run "python manage.py deploy" to deploy the application on GAE.
* (once deployed) run "python manage.py remote shell" to connect to the server remotely.
* Create a super-user with the following commands in the python console:
    
```python    
    from django.contrib.auth.models import User
    su = User.objects.create_user('admin', 'admin@localhost', 'password') 
    su.is_staff = True
    su.is_superuser = True 
    su.save()
```

(you probably want to use a better username/password)

* Visit your app at http://<appname>.appspot.com/


## Adding a prosthetic to the server

* Visit the admin site (/admin/) on your server. Log in. Click the "add" button next to 'prosthetics'.
* Fill in the name and description of your prosthetic. Can be anything.
* The classname needs to be the python classname of the implementation of your prosthetic. The bundled interesting prosthetic classes are "emotional.prosthetic.Emotional" or "dreamer.prosthetic.Dreamer". If your classname is the same as the folder name, but capitalized, you can just use a single word ('emotional' or 'dreamer' in this case).
* Server should be the hostname of the weavrs server you want your prosthetic to talk to. Probably www.weavrs.com.
* Consumer key/secret are from the prosthetic page on the weavrs server. Visit http://www.weavrs.com/developer/ for details.
* Check 'show on homepage' if this is the main prosthetic you want to run on this server. A server can contain multiple prosthetics, but only one will be displayed on the homepage of the server.
* Click "save"
* Return to the root of your site to see the enabled prosthetic.





## Other code

This source tree includes the following other projects:

* django (http://www.djangoproject.com/)
* bleach (http://pypi.python.org/pypi/bleach)
* html5lib (http://code.google.com/p/html5lib/)
* djangotoolbox (https://bitbucket.org/wkornewald/djangotoolbox/src)
* django-nonrel (https://bitbucket.org/wkornewald/django-nonrel/src)
