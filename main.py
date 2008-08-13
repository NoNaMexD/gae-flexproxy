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
import sys
import logging

# import cgitb; cgitb.enable()


# from google.appengine.ext import webapp


# class MainHandler(webapp.RequestHandler):
# 
#   def get(self):
#     self.response.out.write('Hello world!')

class QueryEngine:
    pass

class ProxyError(Exception):
    pass

class ProxyPermissionError(ProxyError):
    pass

class FileQueryEngine(QueryEngine):
    def get_entries(self, ns):
        try:
            efile = open("conf/db_" + ns)
        except IOError:
            return []

        entries = []
        for line in efile:
            entries.append(line.strip())
        efile.close()
        return entries

    def query(self, ns, query):
        entries = self.get_entries(ns)
        for entry in entries:
            if (len(entry) >= 3 and entry[0] == '/' and entry[-1] == '/'):
                if (re.match(entry[1:-1], query)):
                    return True
            else:
                if (entry.lower() == query.lower()):
                    return True
        return False
        
    def query_host(self, query):
        return self.query("hosts", query)
    
    def query_url(self, query):
        return self.query("urls", query)
        
class FlexProxy:
    def __init__(self, filter_hosts=True, filter_urls=True):
        self.query_engine = FileQueryEngine()
        self.filter_hosts = filter_hosts
        self.filter_urls = filter_urls

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

    # determine whether to proxy for this host
    def validate_host(self, host):
        res = self.query_engine.query_host(host)
        return res
        
    # determine whether to proxy for this url
    def validate_url(self, url):
        res = self.query_engine.query_url(url)
        return res

    def check_destination(self, host, url):
        if (not (self.filter_hosts or self.filter_urls)):
           return True
        success = False
        if (self.filter_hosts and self.validate_host(host)):
            success = True
        if (self.filter_urls and self.validate_url(url)):
            success = True
        if (not success):
            logging.info("blowing up")
            raise ProxyPermissionError, ("Destination not allowed", 401)
        return success

    def process(self):
        payload = ''
        if (os.environ.has_key('CONTENT_LENGTH') and len(os.environ['CONTENT_LENGTH'].strip()) > 0):
            length = int(os.environ['CONTENT_LENGTH'].strip())
            if (length > 0):
                payload = sys.stdin.read(length)
        
        headers = {}
        
        method_string = os.environ['REQUEST_METHOD']
        method = self.method_map[ method_string.lower() ]
        
        for hdr in self.copied_headers:
            http_env = 'HTTP_'
            val = None
            if os.environ.has_key('HTTP_' + hdr.upper()):
                val = os.environ['HTTP_' + hdr.upper()]
            elif os.environ.has_key(hdr.upper()):
                val = os.environ[hdr.upper()]

            if (val != None):
                headers[hdr] = val

        m = re.match('^/([^/]+)(/.*)$', os.environ['PATH_INFO'])
        
        if (m == None):
            raise ValueError
        
        host = m.group(1)
        path = m.group(2)

        url = "http://" + host + path

        self.check_destination(host, url)

        if os.environ.has_key('QUERY_STRING'):
            query = os.environ['QUERY_STRING'].strip()
            if (query != ''):
                url = url + '?' + query
        
        try:
            result = urlfetch.fetch(url=url,
                                payload=payload,
                                method=method,
                                headers=headers)
            logging.info("Result code of " + method_string.upper() + " to url " + url + " = " + str(result.status_code) + ", length of body = " + str(len(result.content)))
        except Exception:
            raise ProxyError, ("Can't open page", 404)

        #
        # Process results
        #
        if result.status_code == 200:
            status_msg = "Proxied Request Succeeded"
        else:
            status_msg = "Oops"
        print "Status: " + str(result.status_code) + " " + status_msg

        print "Proxied-Url: " + url        
        
        for name in result.headers:
            if (name.lower() == 'date'): continue
            val = result.headers[name]
            name = self.xlate_header(name)
            print name + ": " + val + "\r\n",

        # end headers and print content

        print

        print result.content

def showError(message, code=500):
      if (not code): code = 401
      print "Status: " + str(code) + " " + message
      print "Content-Length: " + str(len(message))
      print "Content-Type: text/plain"
      print
      print message

def main():
  # application = webapp.WSGIApplication([('/', MainHandler)],
  #                                      debug=True)
  # wsgiref.handlers.CGIHandler().run(application)

  app = FlexProxy(True, True)
  try:
      app.process()
  except ProxyPermissionError, (message, code):
      if (not code): code = 401
      showError("Host or URL not allowed: " + str(message), code)
  except ProxyError, (message, code):
      if (not code): code = 400
      showError("General proxy error: " + str(message), code)
  except Exception, message:
      showError("Unknown error occurred: " + str(message), 500)

if __name__ == '__main__':
  main()
