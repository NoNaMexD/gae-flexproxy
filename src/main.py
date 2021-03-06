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

import sys, os
sys.path.append(os.path.dirname(__file__))

import logging

from org.esquimaux.flexproxy.proxy import *

def showError(message, code=500):
    if (not code): code = 401
    print "Status: " + str(code) + " " + message
    print "Content-Length: " + str(len(message))
    print "Content-Type: text/plain"
    print
    print message

def main():
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
