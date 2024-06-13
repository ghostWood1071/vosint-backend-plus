from fastapi.responses import JSONResponse
from models import MongoRepository
from vosint_ingestion.features.minh.Elasticsearch_main.elastic_main import (
    My_ElasticSearch,
)
from db.init_db import get_collection_client
from bson import ObjectId
from typing import *

my_es = My_ElasticSearch()

categories = {
    "vital": "vital_list",
    "bookmark":  "news_bookmarks", 

}

language_dict = {k:f'keyword_{k}' for k in ['vi', 'en', 'ru', 'cn'] }

def get_news_category(_ids):
    data, _ = MongoRepository().get_many(
        collection_name="News",
        order_spec=["pub_date", "created_at"],
        filter_spec={"_id": {"$in": _ids}},
    )

    result = []
    for item in data:
        item["_id"] = str(item.get("_id"))
        item["pub_date"] = str(item.get("pub_date"))

        result.append(item)

    result = get_optimized(result)

    return result

def get_optimized(result):
    list_fields = [
        "data:html",
        "keywords",
        "source_publishing_country",
        "source_source_type",
        "data:class_linhvuc",
        "data:class_chude",
        "created",
        # "created_at",
        "id_social",
        "modified_at",
    ]

    limit_string = 270

    for record in result:
        try:
            record["data:content"] = record["data:content"][0:limit_string]
            record["data:content_translate"] = record["data:content_translate"][
                0:limit_string
            ]
        except:
            pass
        for key in list_fields:
            record.pop(key, None)
    return result

def get_news_by_category(user_id:str, text_search:str, category:str)->list[str]:
    mongo = MongoRepository().get_one(
            collection_name="users", filter_spec={"_id": user_id}
        )
    ls = []
    return_data = None
    try:
        for new_id in mongo[categories.get(category)]:
            ls.append(str(new_id))
    except:
        pass
    if ls == []:
        return_data = []
    list_id = ls
    if text_search == "" or text_search == None:
        _ids = [ObjectId(item) for item in list_id]
        return_data = get_news_category(_ids)
    return {
        "list_id": list_id, 
        "data": return_data
    }

def get_news_from_cart(news_letter:any, text_search:str):
    # cart is a type of newsletter
    # newsletter has 3 types: gio_tin, linh_vuc, chu_de
    ls = []
    return_data = None
    try:
        for new_id in news_letter["news_id"]:
            ls.append(str(new_id))
    except:
        pass
    if ls == []:
        return_data = []
    list_id = ls

    if text_search == "" or text_search == None:
        _ids = [ObjectId(item) for item in list_id]
        return_data = get_news_category(_ids)
    return {
        "list_id": list_id,
        "return_data": return_data
    }

def get_source_names(type, id_source):
    #id_source la id_nguon_nhom_nguon
    list_source_name = None
    if type == "source":
        name = MongoRepository().get_one(
            collection_name="info", filter_spec={"_id": id_source}
        )["name"]
        list_source_name = []
        list_source_name.append('"' + name + '"')
    elif type == "source_group":
        source_group = MongoRepository().get_one(
            collection_name="Source", filter_spec={"_id": id_source}
        )
        name = source_group.get("news")
        list_source_name = []
        for i in name:
            list_source_name.append('"' + i["name"] + '"')
    return list_source_name


#--------------- build query ---------------------
def get_date(start_date, end_date):
    try:
        start_date = (
            start_date.split("/")[2]
            + "-"
            + start_date.split("/")[1]
            + "-"
            + start_date.split("/")[0]
            + "T00:00:00Z"
        )
    except:
        pass

    try:
        end_date = (
            end_date.split("/")[2]
            + "-"
            + end_date.split("/")[1]
            + "-"
            + end_date.split("/")[0]
            + "T00:00:00Z"
        )
    except:
        pass
    return start_date, end_date

def build_keyword(keyword_source, first_flat):
    query = ""
    try:
        for key_line in keyword_source:
            if first_flat == 1:
                first_flat = 0
                query += "("
            else:
                query += " + ("
            include_keys = key_line.split(",")
            for key in include_keys:
                #query += "+" + '"' + key + '"'
                key = key.strip(" ")
                query += f'"{key}" | '
            query = query.strip("| ")
            query += ")"
    except:
        pass
    return query, first_flat

def build_exclude_keywords(newsletter, *langs:list[str]):
    query_set = []
    query  = ""
    for lang in langs:
        lang_key = language_dict.get(lang)
        exclude_phrase = newsletter[lang_key].get("exclusion_keyword")
        if exclude_phrase not in [None, ""]:
            exclude_keys = [f'"{key.strip(" ")}"' for key in exclude_phrase.split(",")]
            exclude_query = " + ".join(exclude_keys)
            if exclude_query != "":
                query_set.append(exclude_query)
    if len(query_set) > 0:
        query = f' - ({" + ".join(query_set)})'
    return query
    
            

def build_keyword_by_lang(newsletter, lang, first_flat):
    lang_key = language_dict.get(lang)
    key_source = newsletter[lang_key]["required_keyword"]
    # exclude_keys = newsletter[lang_key]["exclusion_keyword"]
    return build_keyword(key_source, first_flat)

def combine_keyword(*keywords):
    first_lang = 1
    query = ""
    for keyword in keywords:
        if keyword != "":
            if first_lang == 1:
                first_lang = 0
                query += "(" + keyword + ")"
            else:
                query += "| (" + keyword + ")"
    return query

def validate_read(pipeline_dtos, is_get_read_state):
    for i in range(len(pipeline_dtos)):
        try:
            pipeline_dtos[i]["_source"]["_id"] = pipeline_dtos[i]["_source"]["id"]
        except:
            pass
        pipeline_dtos[i] = pipeline_dtos[i]["_source"].copy()
    if is_get_read_state:
        news_ids = [ObjectId(row["id"]) for row in pipeline_dtos]
        raw_isreads, _ = MongoRepository().get_many("News", {"_id": {"$in": news_ids}})
        isread = {}
        for raw_isread in raw_isreads:
            isread[str(raw_isread["_id"])] = raw_isread.get("list_user_read")
        for row in pipeline_dtos:
            row["list_user_read"] = isread.get(row["_id"])

def build_search_query_by_keyword(news_letter):
    query = ""
    if news_letter["is_sample"]:
            first_flat = 1
            query, first_flat = build_keyword(news_letter["required_keyword_extract"], first_flat)
       
    else:  #lay tin theo tu khoa cua nguoi dung tu dinh ngia
        query = ""
        ### vi
        first_flat = 1
        query_vi, first_flat = build_keyword_by_lang(news_letter, "vi", first_flat)
        ### cn
        query_cn, first_flat = build_keyword_by_lang(news_letter, "cn", first_flat)
        ### ru
        query_ru, first_flat = build_keyword_by_lang(news_letter, "ru", first_flat)
        ### cn
        query_en, first_flat = build_keyword_by_lang(news_letter, "en", first_flat)
        ## combine all keyword
        exclude_query = build_exclude_keywords(news_letter, "vi", "cn", "ru", "en")
        query = combine_keyword(query_vi, query_cn, query_ru, query_en) + exclude_query
    return query

def get_news_from_newsletter_id__(
    list_id=None, # a list of news id that can limit the result of elastic
    type=None,
    id_nguon_nhom_nguon=None,
    page_number=1,
    page_size=100,
    start_date: str = None,
    end_date: str = None,
    sac_thai: str = None,
    language_source: str = None,
    news_letter_id: str = "",
    text_search=None,
    vital: str = "",
    bookmarks: str = "",
    user_id=None,
    is_get_read_state=False,
    list_fields=None,
):
    
    query = None
    index_name = "vosint"

    # date-------------------------------------------
    start_date, end_date = get_date(start_date, end_date)
    # language--------------------------------------------------------
    if language_source:
        language_source_ = language_source.split(",")
        language_source = []
        for i in language_source_:
            language_source.append(i)
    # lay tin quan trong ---tin quan trọng -------------------------------------------------
    if vital == "1":
        result_search = get_news_by_category(user_id, text_search, "vital")
        if result_search.get("data") is not None:
            return result_search.get("data")
        list_id = result_search.get("list_id")
    # lay tin danh dau ---tin đánh dấu ---------------------------------------------------
    elif bookmarks == "1":
        result_search = get_news_by_category(user_id, text_search, "bookmark")
        if result_search.get("data") is not None:
            return result_search.get("data")
        list_id = result_search.get("list_id")

    # chu de/get newsletter --------------------------------------------------
    if news_letter_id != "" and news_letter_id != None:
        news_letter = MongoRepository().get_one(
            collection_name="newsletter", filter_spec={"_id": news_letter_id}
        )
    
    # nếu là giỏ tin
    if news_letter_id != "" and news_letter["tag"] == "gio_tin":
        result_search = get_news_from_cart(news_letter, text_search)
        if result_search.get("return_data") is not None:
            return result_search.get("return_data")
        list_id = result_search.get("list_id")

    # nếu không là giỏ tin
    if news_letter_id != "" and news_letter["tag"] != "gio_tin":
        #lay tin theo tu khoa trich tu van ban mau
        query = build_search_query_by_keyword(news_letter)

    list_source_name = get_source_names(type, id_nguon_nhom_nguon)

    if text_search == None and list_source_name == None:
        pipeline_dtos = my_es.search_main(
            index_name=index_name,
            query=query,
            gte=start_date,
            lte=end_date,
            lang=language_source,
            sentiment=sac_thai,
            list_id=list_id,
            size=(int(page_number)) * int(page_size),
            list_fields=list_fields
        )
    elif text_search == None and list_source_name != None:
        pipeline_dtos = my_es.search_main(
            index_name=index_name,
            query=query,
            gte=start_date,
            lte=end_date,
            lang=language_source,
            sentiment=sac_thai,
            list_id=list_id,
            list_source_name=list_source_name,
            size=(int(page_number)) * int(page_size),
            list_fields=list_fields
        )
    else: #text_search != None and list_source_name != None
        if text_search !=None and text_search != "":
            query = f'({query}) + ("{text_search}")'

        if list_source_name == None:
            pipeline_dtos = my_es.search_main(
                index_name=index_name,
                query=query,
                gte=start_date,
                lte=end_date,
                lang=language_source,
                sentiment=sac_thai,
                list_id=list_id,
                size=(int(page_number)) * int(page_size),
                list_fields=list_fields
            )
        else:
            pipeline_dtos = my_es.search_main(
                index_name=index_name,
                query=query,
                gte=start_date,
                lte=end_date,
                lang=language_source,
                sentiment=sac_thai,
                list_id=list_id,
                list_source_name=list_source_name,
                size=(int(page_number)) * int(page_size),
                list_fields=list_fields
            )
        if list_id == None:
            list_id = []

        for i in range(len(pipeline_dtos)):
            list_id.append(pipeline_dtos[i]["_source"]["id"])

   
    validate_read(pipeline_dtos, is_get_read_state)
    
    return pipeline_dtos
