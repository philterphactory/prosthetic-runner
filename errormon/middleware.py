from errormon.models import store_exception

class ExceptionStoreMiddleware(object):
    #noinspection PyUnusedLocal
    def process_exception(self, request, exception):
        return store_exception(request)
