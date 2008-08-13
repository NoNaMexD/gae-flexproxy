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

# import cgitb; cgitb.enable()


# from google.appengine.ext import webapp


# class MainHandler(webapp.RequestHandler):
# 
#   def get(self):
#     self.response.out.write('Hello world!')

class QueryEngine:
    z =  "foo"

class ProxyPermissionError(Exception):
    z = "foo"

class FileQueryEngine(QueryEngine):
    def get_entries(self, ns):
        try:
            efile = open("files/db_" + ns)
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
    def __init__(self, filter_hosts=True, filter_urls=False):
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
        return True

    def process(self):
        payload = ''
        if (os.environ.has_key('CONTENT_LENGTH') and len(os.environ['CONTENT_LENGTH'].strip()) > 0):
            length = int(os.environ['CONTENT_LENGTH'].strip())
            if (length > 0):
                payload = sys.stdin.read(length)
        
        headers = {}
        
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

        m = re.match('^/([^/]+)(/.*)$', os.environ['PATH_INFO'])
        
        if (m == None):
            raise ValueError
        
        host = m.group(1)
        path = m.group(2)
        
        if (self.filter_hosts and not self.validate_host(host)):
            raise ProxyPermissionError, ("host not allowed", 401)
        
        url = "http://" + host + path
        
        if (self.filter_urls and not self.validate_url(url)):
            raise ProxyPermissionError, ("URL not allowed", 401)

        if os.environ.has_key('QUERY_STRING'):
            query = os.environ['QUERY_STRING'].strip()
            if (query != ''):
                url = url + '?' + query
        
        result = urlfetch.fetch(url=url,
                                payload=payload,
                                method=method,
                                headers=headers)

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

def main():
  # application = webapp.WSGIApplication([('/', MainHandler)],
  #                                      debug=True)
  # wsgiref.handlers.CGIHandler().run(application)

  app = FlexProxy()
  try:
      app.process()
  except ProxyPermissionError, (message, code):
      if (not code): code = 401
      body = "Host or URL not allowed: " + str(message)
      print "Status: " + str(code) + " " + message
      print "Content-Length: " + str(len(body))
      print "Content-Type: text/plain"
      print
      print body
  except Exception, message:
      body = "Unknown error occurred: " + str(message)
      print "Status: 500 Unknown Error"
      print "Content-Length: " + str(len(body))
      print "Content-Type: text/plain"
      print
      print body

if __name__ == '__main__':
  main()
