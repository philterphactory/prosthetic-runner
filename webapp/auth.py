import logging
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from gaeauth.backends import GoogleAccountBackend
from google.appengine.api import users

class HackyGoogleAccountBackend(GoogleAccountBackend):

    def authenticate(self, **credentials):
        user = super(HackyGoogleAccountBackend,self).authenticate(**credentials)
        if not user:
            return None

        # if a user was created as an admin but is no longer an admin, fix. Also, the
        # other way round.
        current = users.is_current_user_admin()
        db = (user.is_superuser and user.is_staff)
        if current != db:
            user.is_superuser = current
            user.is_staff = current
            user.save()

        return user
