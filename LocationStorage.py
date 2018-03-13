from tinydb import TinyDB, Query
import time

class SaverTest(object):
    def test_print(self):
        print "Test has passed"

class Saver(object):
    '''Class that manages location presistance'''
    db = TinyDB('locationDB.json')

    def insert_location_info(self, location_id):
        '''stores  location info'''
        if self.contains_location_id(location_id) == False:
            current_date = time.time()
            self.db.insert({'id': location_id, 'timestamp': current_date})
            return True
        else:
            print "Location id already exists"
            return False

    def fetch_lastest_loc_id(self):
        '''fetching location id with the latest date'''
        for item in self.db:
            print item

    def contains_location_id(self, location_id):
        '''checks if location id is already in the base'''
        location = Query()
        result = self.db.search(location.id == location_id)
        if not result:
            return False
        else:
            return result.count > 0

    def remove_all_files(self):
        '''purges all files'''
        self.db.purge()
