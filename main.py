#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#




import wsgiref.handlers
import cgi
from google.appengine.api import urlfetch
import urllib
import os
import re

# import cgitb; cgitb.enable()


# from google.appengine.ext import webapp


# class MainHandler(webapp.RequestHandler):
# 
#   def get(self):
#     self.response.out.write('Hello world!')


class FlexProxy:
    # def __init__(baseurl):
    #     self.baseurl = baseurl

    copied_headers = [
        'Server',
        'Content-Length',
        'Content-Type',
        'Date',
        'X-Powered-By',
        'Accept',
        'Accept-Language',
        'Accept-Encoding',
        'Cache-Control',
        'Pragma'
    ]
    
    method_map = {
        'get':     urlfetch.GET,
        'post':    urlfetch.POST,
        'head':    urlfetch.HEAD,
        'put':     urlfetch.PUT,
        'delete':  urlfetch.DELETE
    }

    def xlate_header(self, hdr):
        for name in self.copied_headers:
            if hdr.lower() == name.lower(): return name
        return hdr

    def process(self):
        data = {
          "api_key": "62efb891fc6ae7200a2699c566503735",
          "user_app_key": "8425ab6700ac14eacdc77acf3283d69b-1217912257"
        }
        encoded_data = urllib.urlencode(data)
        
        headers = {}
        
        # XXX: lame
        # if (os.environ['HTTP_METHOD'].lower() == 'get'):
        #     method = urlfetch.GET
        # else:
        #     method = urlfetch.POST
        
        method = self.method_map[ os.environ['REQUEST_METHOD'].lower() ]
        
        for hdr in self.copied_headers:
            http_env = 'HTTP_'
            val = None
            if os.environ.has_key('HTTP_' + hdr.upper()):
                val = os.environ['HTTP_' + hdr.upper()]
            elif os.environ.has_key(hdr.upper()):
                val = os.environ[hdr.upper()]

            if (val != None):
                headers[hdr] = val
        
        url="http://api.ping.fm/v1/user.latest"
        
        m = re.search('^/([^/]+)(/.*)$', os.environ['PATH_INFO'])
        
        result = urlfetch.fetch(url,
                                payload=encoded_data,
                                method=method,
                                headers=headers)

        #
        # Process results
        #

        for name in result.headers:
            if (name.lower() == 'date'): continue
            val = result.headers[name]
            name = self.xlate_header(name)
            print name + ": " + val + "\r\n",

        print

        # for var in os.environ.keys():
        #     print var + ": " + os.environ.get(var) + "\n"

        print result.content

def main():
  # application = webapp.WSGIApplication([('/', MainHandler)],
  #                                      debug=True)
  # wsgiref.handlers.CGIHandler().run(application)

  app = FlexProxy()
  app.process()

if __name__ == '__main__':
  main()
