from vosint_ingestion.models import MongoRepository
from typing import *
import traceback
from bson.objectid import ObjectId

def add_word(word:Dict[str, Any]):
    try:
        in_word = MongoRepository().get_one("dictionary", {"value": word.get("value")}, {"_id": 1})
        if in_word:
            raise Exception(f"word: {word.get('value')} is existed")
        inserted = MongoRepository().insert_one("dictionary", word)
        return inserted
    except Exception as e:
        traceback.print_exc()
        raise e

def update_word(word:Dict[str, Any]):
    try:
        in_words = MongoRepository().get_many(
            "dictionary", 
            {
               "$or": [
                   {"_id": ObjectId(word.get("id"))},
                   {"value": word.get("value")}
                ]
            }, 
            {"_id": 1, "value": 1}
        )[0]
        name_err = Exception(f"word: {word.get('value')} is not existed")
        if len(in_words) == 0:
            raise name_err
        
        for in_word in in_words:
            if in_word.get("value") == word.get("value") and str(in_word.get("_id")) != word.get("id"):
                raise name_err
        change = {"value": word.get("value")}
        if word.get("mode") == 0:
            change["synonyms"] = word.get("synonyms")
        else:
            change["multimeans"] = word.get("multimeans")

        updated = MongoRepository().update_many(
            "dictionary", 
            {"_id": ObjectId(word.get("id"))},
            {"$set": change}
        )
        return updated
    except Exception as e:
        traceback.print_exc()
        raise e       
    
def delete_word(ids:List[str]):
    try:
        word_filter = [ObjectId(id) for id in ids]
        deleted = MongoRepository().delete_many("dictionary", {"_id": {"$in": word_filter}})
        return deleted
    except Exception as e:
        traceback.print_exc()
        raise e
    
def search_word(
    search_text:str = None,
    mode:int = 0|1,
    page_size: int = 50,
    page_index: int = 1
):
    try:
        word_filter = {}
        paginate = {
            "skip": (page_index - 1) * page_size,
            "limit": page_size
        }
        project = {
            "_id": 1,
            "value": 1
        }
        if mode == 0:
            project["synonyms"] = 1

        if mode == 1:
            project["multimeans"] = 1

        if search_text: 
            word_filter["value"] = {"$regex": search_text, "$options": "i"}
        
        results = MongoRepository().get_many(
            "dictionary", 
            word_filter, 
            ["created_at-desc"], 
            paginate, 
            projection=project
        )
        return results
    except Exception as e:
        traceback.print_exc()
        raise e
    
    