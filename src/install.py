import sys, os
sys.path.append(os.path.dirname(__file__))

from org.esquimaux.flexproxy.store.datastore_queryengine import *

def main():
    ds = DatastoreQueryEngine()
    ds.seed()
    logging.info("Seeded datastore")
    print "Done"

if __name__ == '__main__':
    main()

