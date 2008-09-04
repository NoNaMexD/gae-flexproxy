import os, re, sys, logging

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
from org.esquimaux.flexproxy.store.queryengine import QueryEngine

class ProxyACL(db.Model):
    name = db.StringProperty(required=False)
    item = db.StringProperty(required=True, choices=set(["url", "host"]))
    operator = db.StringProperty(required=True, choices=set(["exact", "regex"]))
    operand = db.StringProperty(required=True)
    added = db.DateTimeProperty(auto_now_add=True)
    added_by = db.UserProperty()

class DatastoreQueryEngine(QueryEngine):
    def seed(self):
        entry = ProxyACL(name="testing",
                         item="host",
                         operator="exact",
                         operand="api.ping.fm",
                         added_by=users.get_current_user())
        entry.put()

    def query(self, ns, item):
        key = "query_" + ns + "_" + item
        cached = memcache.get(key)
        if (cached is not None):
            return bool(cached)
        res = self._realquery(ns, item)
        # cache for 10 minutes
        memcache.set(key, str(res), 600)
        return res

    def _realquery(self, ns, item):
        query = ProxyACL.all()

        query.filter('item =', ns)
        
        query.fetch(500)

        for result in query:
            logging.debug("Checking on " + result.operand + ", op=" + result.operator)
            res = self._match(item, result.operand, result.operator)
            if (res):
                return True
        
        return False

    def query_host(self, query):
        return self.query("host", query)
    
    def query_url(self, query):
        return self.query("url", query)

# pet = Pet(name="Fluffy",
#           type="cat",
#           owner=users.get_current_user())
# pet.weight_in_pounds = 24
# pet.put()
# 
#   user_pets = db.GqlQuery("SELECT * FROM Pet WHERE pet.owner = :1",
#                           users.get_current_user())
#   for pet in user_pets:
#     pet.spayed_or_neutered = True
# 
#   db.put(user_pets)
#   
#  
# query = Story.all()
# 
# query.filter('title =', 'Foo')
# query.order('-date')
# query.ancestor(key)
# 
# # These methods can be chained together on one line.
# query.filter('title =', 'Foo').order('-date').ancestor(key)