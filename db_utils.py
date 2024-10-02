import pymongo

from constants import DATABASE_NAME, SQUADS_COLLECTION, MATCH_LIST_COLLECTION, BALL_BY_BALL_DATA_COLLECTION, LINEUPS_COLLECTION


class MongoDBConnector(object):
    
    def __init__(self, DB_URI) -> None:
        self.client = pymongo.MongoClient(DB_URI)
        self.data_db = self.client.get_database(DATABASE_NAME)
        self.squads_collection = self.get_or_create_collection(SQUADS_COLLECTION) 
        self.match_list_collection = self.get_or_create_collection(MATCH_LIST_COLLECTION)
        self.bbb_data_collection = self.get_or_create_collection(BALL_BY_BALL_DATA_COLLECTION)
        self.lineups_collection = self.get_or_create_collection(LINEUPS_COLLECTION)
    
    def get_or_create_collection(self, collection_name):
        if collection_name in self.data_db.list_collection_names():
            return self.data_db.get_collection(collection_name)
        else:
            return self.data_db.create_collection(collection_name)
        
    def get_data(self, collection, filter_in=None):
        try:
            items = collection.find(filter=filter_in)
            return list(items)
        except Exception as e:
            print(e)
            return []
    
    def get_squads(self):
        return self.get_data(self.squads_collection)    
    
    def get_matches(self):
        return self.get_data(self.match_list_collection)
    
    def get_single_match_details(self, match_id):
        filter_in = {"match_id": match_id}
        
        match_details = self.match_list_collection.find_one(filter_in)
        
        if match_details is None:
            return None
        
        bbb_data = self.get_data(self.bbb_data_collection, filter_in=filter_in)
        bbb_data.sort(key=lambda x: x["ball_id"])
        
        lineups = self.get_data(self.lineups_collection, filter_in=filter_in)
        lineups.sort(key=lambda x: x["player_name"])
                
        match_details["ball_by_ball_data"] = bbb_data
        match_details["lineups"] = lineups
        
        return match_details
    
    def add_new_matches(self, matches_list):
        self.match_list_collection.insert_many(matches_list)
        
    def add_new_lineups(self, lineups_list):
        self.lineups_collection.insert_many(lineups_list)
        
    def add_new_bbb(self, bbb_list):
        self.bbb_data_collection.insert_many(bbb_list)
        
    def fully_reset_db(self):
        self.bbb_data_collection.delete_many({})
        self.lineups_collection.delete_many({})
        self.match_list_collection.delete_many({})
        

if __name__ == "__main__":
    from constants import DB_URI
    
    connector = MongoDBConnector(DB_URI=DB_URI)

    print(connector.data_db.list_collection_names())
    print(connector.get_squads())
    print(connector.get_matches())
    print(connector.get_single_match_details("INDIA-WOMEN_PAKISTAN-WOMEN_20240924"))
    
    DELETE = False
    
    if DELETE:
        connector.fully_reset_db()

