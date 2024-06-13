from bson.objectid import ObjectId
from models import HBaseRepository, MongoRepository
import sys
sys.path.insert(0, "/home/ds1/vosint")

from vosint_ingestion.nlp.hieu.vosintv3_text_clustering_main.code_doan.src.update_chude import update_chude
from vosint_ingestion.nlp.hieu.vosintv3_text_clustering_main.code_doan.src.create_db_chude import create_db_chude
from vosint_ingestion.nlp.hieu.vosintv3_text_clustering_main.code_doan.src.create_db_linhvuc import create_db_linhvuc
from vosint_ingestion.nlp.hieu.vosintv3_text_clustering_main.code_doan.src.update_linhvuc import update_linhvuc

# from vosint_ingestion.nlp.hieu.vosintv3_text_clustering_main.code_doan.src.create_db_object import create_db_object
# from vosint_ingestion.nlp.hieu.vosintv3_text_clustering_main.code_doan.src.update_object import update_object

class NlpService:

    def __init__(self):
        self.__mongo_repo = MongoRepository()
    
    def update(self):
        try:
            create_db_chude()
            create_db_linhvuc()
            return {"success": "True"}
        except:
            return {"success": "False"}
    def nlp_update_list_id(self,_id):
        try:
            list_rs = []
            mongo = MongoRepository()
            id_chude = _id
            a = mongo.get_one(collection_name="newsletter",filter_spec={"_id":id_chude})
            if a['tag'] == "chu_de":
                query = { "data:class_chude": { "$regex": ".*"+id_chude+".*" } }
                results = mongo.get_many_d('News',filter_spec=query,filter_other={"_id":1})

                new_id = []
                for i in results[0]:
                    new_id.append(i['_id'])
                mongo.update_one(collection_name='newsletter',doc={"_id":id_chude,"news_id":new_id})
            
            elif a['tag'] == "linh_vuc":
                query = { "data:class_chude": { "$regex": ".*"+id_chude+".*" } }
                results = mongo.get_many_d('News',filter_spec=query,filter_other={"_id":1})

                new_id = []
                for i in results[0]:
                    new_id.append(i['_id'])
                mongo.update_one(collection_name='newsletter',doc={"_id":id_chude,"news_id":new_id})

            return {"success": "True"}
        except:
            return {"success": "False"}
        


    def nlp_update_list_all(self):
        try:
            list_rs = []
            mongo = MongoRepository()

            query = {
            "$and": [
                #{"required_keyword": {"$exists": True}},
                #{"exclusion_keyword": {"$exists": True}},
                {"news_samples": {"$exists": True}},
                {"news_samples": {"$ne": None}},
                {"news_samples": {"$ne": []}}
                    ]
                }
            
            query = {}

            new_letter, _ = mongo.get_many(
                "newsletter",
                query
            )
            _id = []
            for i in new_letter:
                _id.append(str(i["_id"]))



            for id_chude in _id:
                a = mongo.get_one(collection_name="newsletter",filter_spec={"_id":id_chude})
                if a['tag'] == "chu_de":
                    query = { "data:class_chude": { "$regex": ".*"+id_chude+".*" } }
                    results = mongo.get_many_d('News',filter_spec=query,filter_other={"_id":1})

                    new_id = []
                    for i in results[0]:
                        new_id.append(i['_id'])
                    mongo.update_one(collection_name='newsletter',doc={"_id":ObjectId(id_chude),"news_id":new_id})
                
                elif a['tag'] == "linh_vuc":
                    query = { "data:class_chude": { "$regex": ".*"+id_chude+".*" } }
                    results = mongo.get_many_d('News',filter_spec=query,filter_other={"_id":1})

                    new_id = []
                    for i in results[0]:
                        new_id.append(i['_id'])
                    mongo.update_one(collection_name='newsletter',doc={"_id":ObjectId(id_chude),"news_id":new_id})

            return {"success": "True"}
        except:
            return {"success": "False"}

    # def get_id_chude(self,user_id: str,title_chu_de: str):
    #     a = self.__mongo_repo.get_one(collection_name='newsletter',filter_spec={"title":title_chu_de,"user_id":user_id}\
    #         ,filter_other= {"_id": 1})
    #     return str(a['_id'])
    # def nlp_update_chude_text():
    #     try:
    #         create_db_chude()
    #         update_chude()
    #         create_db_linhvuc()
    #         update_linhvuc()
    #         create_db_object()
    #         update_object()
    #         return 'True'
    #     except:
    #         return "False"
    # def nlp_chude(self, id_chude,order_spec,pagination_spec):
    #     # id_chude = self.get_id_chude(ObjectId(user_id),title_chu_de)
        
    #     # query = { "news_id_chude": { "$regex": ".*"+id_chude+".*" } }
    #     # results = self.__mongo_repo.get_many_d('News',filter_spec=query,order_spec=order_spec,
    #     #                                                    pagination_spec=pagination_spec,filter_other={"_id":0})

    #     query = { "data:class_chude": { "$regex": ".*"+id_chude+".*" } }
    #     results = self.__mongo_repo.get_many_d('News',filter_spec=query,order_spec=order_spec,
    #                                                        pagination_spec=pagination_spec,filter_other={"_id":1})

    #     for i in results[0]: 
    #         i['_id'] = str(i['_id'])
            

    #     # results = self.__mongo_repo.get_many_d('newsletter',filter_spec={'_id':id_chude},order_spec=order_spec,
    #     #                                                    pagination_spec=pagination_spec,filter_other={"news_id_chude":1})
    #     return results
