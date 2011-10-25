import StringIO
import datetime
import logging
import sys
import traceback
from django import http
from django.contrib.auth.models import User, AnonymousUser
from django.db import models
from errormon import UnreportedException


class ExceptionModel(models.Model):
    """A record of an exception that occurred."""
    occurred_at = models.DateTimeField(default=datetime.datetime.now())
    status_code = models.IntegerField(default=500)

    exc_type = models.CharField(null=True, blank=True, max_length=1023)
    exc_value = models.TextField(null=True, blank=True)
    exc_traceback = models.TextField(null=True, blank=True)

    req_host = models.CharField(null=True, blank=True, max_length=256)
    req_secure = models.NullBooleanField(null=True, blank=True)
    req_method = models.CharField(null=True, blank=True, max_length=32)
    req_path = models.CharField(null=True, blank=True, max_length=2048)
    req_headers = models.TextField(null=True, blank=True)
    req_data = models.TextField(null=True, blank=True)
    req_user = models.ForeignKey(User, null=True, blank=True)

    def __repr__(self):
        #noinspection PyStringFormat
        return u"""<ExceptionModel:
    occurred_at=%(occurred_at)s
    status_code=%(status_code)s
    path=%(req_path)s
    exc_type=%(exc_type)s
    exc_value=%(exc_value)s
    exc_traceback:
%(exc_traceback)s
    request:
%(req_method)s %(req_path)s
%(req_headers)s

%(req_data)s>""" % self.__dict__


def store_exception(request=None):
    try:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if isinstance(exc_value, (UnreportedException, http.Http404)):
            return None

        m = ExceptionModel()

        exc_type, exc_value, exc_traceback = sys.exc_info()
        m.exc_type = exc_type.__name__
        m.exc_value = exc_value
        m.exc_traceback = "".join(traceback.format_tb(exc_traceback)).strip()

        m.status_code = int(
            getattr(exc_value, "status_code",
                getattr(exc_value, "code",
                        isinstance(exc_value, int) and exc_value or 500
                )
            )
        )

        if request:
            m.req_host = request.get_host()
            m.req_secure = request.is_secure()
            m.req_method = request.method
            m.req_path = request.get_full_path()
            headers = StringIO.StringIO()
            for k,v in request.META.iteritems():
                # does not encode i.e. newlines properly so in edge cases will not quite be reparseable/replayable,
                #     which I've decided is ok, since even httplib breaks the rules here
                if k.startswith("wsgi"):
                    continue
                headers.write(k)
                headers.write(": ")
                headers.write(v)
                if not v.endswith("\n"):
                    headers.write("\r\n")
            m.req_headers = headers.getvalue()
            del headers
            m.req_data = request.raw_post_data

            u = request.user
            if not isinstance(u, AnonymousUser):
                m.req_user = u

        m.save()
    except Exception, e:
        logging.error("Exception occurred saving exception to store", e)
    finally:
        # ignore all exceptions raised in this middleware...report original
        return None
