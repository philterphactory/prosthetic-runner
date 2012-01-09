from google.appengine.ext import webapp as wa
from google.appengine.ext.zipserve import ZipHandler, main

application = wa.WSGIApplication([('/([^/]+)/(.*)', ZipHandler)])

if __name__ == '__main__':
    main()
