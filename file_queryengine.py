from queryengine import *
from google.appengine.api import memcache
import cgi, urllib
import os, re, sys, logging

class FileQueryEngine(QueryEngine):
    def get_entries(self, ns):
        logging.info("opening file conf/db_" + ns)
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
        key = "query_" + ns + "_" + query
        cached = memcache.get(key)
        if (cached is not None):
            return bool(cached)
        res = self._realquery(ns, query)
        # cache for 10 minutes
        memcache.set(key, str(res), 600)
        return res

    def _realquery(self, ns, query):
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