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




# import wsgiref.handlers
import cgi
from google.appengine.api import urlfetch
import urllib

# import cgitb; cgitb.enable()


# from google.appengine.ext import webapp


# class MainHandler(webapp.RequestHandler):
# 
#   def get(self):
#     self.response.out.write('Hello world!')


class FlexProxy:
    # def __init__(baseurl):
    #     self.baseurl = baseurl

    headermap = {
        'server': 'Server',
        'content-length': 'Content-Length',
        'content-type': 'Content-Type',
        'date': 'Date',
        'x-powered-by': 'X-Powered-By'
    }

    def process(self):
        data = {
          "api_key": "62efb891fc6ae7200a2699c566503735",
          "user_app_key": "8425ab6700ac14eacdc77acf3283d69b-1217912257"
        }
        encoded_data = urllib.urlencode(data)
        result = urlfetch.fetch(url="http://api.ping.fm/v1/user.latest",
                                payload=encoded_data,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'})

        for name in result.headers:
            if (name.lower() == 'date'): continue
            val = result.headers[name]
            if (name in self.headermap): name = self.headermap[name]
            print name + ": " + val + "\r\n",

        #print "Content-Length: " + str(len(result.content))
        #print "Content-Type: " + result.headers['content-type']

        print
        print result.content

def main():
  # application = webapp.WSGIApplication([('/', MainHandler)],
  #                                      debug=True)
  # wsgiref.handlers.CGIHandler().run(application)

  app = FlexProxy()
  app.process()

if __name__ == '__main__':
  main()
