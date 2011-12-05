import logging
import os
import sys
from errormon.models import store_exception

class ExceptionStoreMiddleware(object):
    #noinspection PyUnusedLocal
    def process_exception(self, request, exception):
        return store_exception(request)

#noinspection PyUnusedLocal
class IdeDebugMiddleware(object):
    """Incredibly hacky middleware that effectively disables the GAE dev appserver sandbox."""
    def disable_sandbox(self):
        try:
            # mostly disable the sandbox, mostly so that pydev debugging works ok
            from google.appengine.tools import dev_appserver
            changed = False
            for p in sys.path:
                if not p in dev_appserver.FakeFile._application_paths:
                    changed = True
                    dev_appserver.FakeFile._application_paths.add(os.path.abspath(p))
            if changed:
                logging.info("Enabling IDE debugging")
                dev_appserver.FakeFile._availability_cache = {}
        except Exception:
            logging.error("Enabling IDE debugging failed", exc_info=sys.exc_info())
            pass

    def process_request(self, *args, **kwargs):
        self.disable_sandbox()
        return None

    def process_request(self, *args, **kwargs):
        self.disable_sandbox()
        return None
