from fastapi import APIRouter
from bson import ObjectId
import requests
from fastapi.responses import JSONResponse
import time
from .jobcontroller import JobController
from datetime import datetime
from typing import List
from models import MongoRepository
from fastapi_jwt_auth import AuthJWT
from fastapi.params import Body, Depends
from vosint_ingestion.features.minh.Elasticsearch_main.elastic_main import (
    My_ElasticSearch,
)
from datetime import datetime

my_es = My_ElasticSearch()
from pydantic import BaseModel
from db.init_db import get_collection_client
from vosint_ingestion.features.job.services.get_news_from_elastic import (
    get_news_from_newsletter_id__,
    build_search_query_by_keyword
)
from core.config import settings
from datetime import timedelta
import asyncio
import json
import re

ttxvn_client = get_collection_client("ttxvn")


class Translate(BaseModel):
    lang: str
    content: str


class elt(BaseModel):
    page_number: int = 1
    page_size: int = 30
    newsletter_id: str = ""  # sử dụng trong bảo newletter ko cần tự làm newList
    newList: List[
        str
    ] = []  # Trong trường hợp phát sinh, tìm kiếm trong 1 newslist nào đó
    groupType: str = None  # vital or bookmarks or ko truyền
    search_Query: str = None  # "abc" người dùng nhập
    startDate: str = None  # 17/08/2023
    endDate: str = None  # 17/08/2023
    langs: str = None  #'vi','en', 'ru' ví dụ vi,en hoặc en,ru hoặc vi
    sentiment: str = None  #'0' trung tinh, '1' tích cực, '2' tiêu cực, all ko truyền
    id_nguon_nhom_nguon: str = None  #'id source' or 'id source_group'
    type: str = None  #'source' or 'source_group'


job_controller = JobController()
router = APIRouter()


@router.post("/api/get_news_from_ttxvn")
def get_news_from_ttxvn(
    page_number=1,
    page_size=50,
    start_date: str = None,
    end_date: str = None,
    sac_thai: str = None,
    language_source: str = None,
    text_search=None,
):
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
            + "T23:59:59Z"
        )
    except:
        pass
    pipeline_dtos = my_es.search_main_ttxvn(
        index_name="vosint_ttxvn",
        query=text_search,
        gte=start_date,
        lte=end_date,
        lang=language_source,
        sentiment=sac_thai,
        size=(int(page_number)) * int(page_size),
    )

    for i in range(len(pipeline_dtos)):
        try:
            pipeline_dtos[i]["_source"]["_id"] = pipeline_dtos[i]["_source"]["id"]
        except:
            pass
        pipeline_dtos[i] = pipeline_dtos[i]["_source"].copy()

    news_ids = [ObjectId(row["id"]) for row in pipeline_dtos]
    raw_is_reads, _ = MongoRepository().get_many("ttxvn", {"_id": {"$in": news_ids}})
    is_read = {}
    for raw_is_read in raw_is_reads:
        is_read[str(raw_is_read["_id"])] = raw_is_read.get("list_user_read")
    for row in pipeline_dtos:
        row["list_user_read"] = is_read.get(row["_id"])

    return JSONResponse(
        {
            "success": True,
            "total_record": len(pipeline_dtos),
            "result": pipeline_dtos[
                (int(page_number) - 1)
                * int(page_size) : (int(page_number))
                * int(page_size)
            ],
        }
    )

    # data = MongoRepository().get_one(
    #     "ttxvn", {"_id": ObjectId("6541e5b00aae56bc757b8109")}
    # )
    # data["_id"] = str(data["_id"])
    # data["PublishDate"] = str(data["PublishDate"])
    # data["Created"] = str(data["Created"])

    # return JSONResponse(
    #     {
    #         "success": True,
    #         "total_record": len(pipeline_dtos),
    #         "result": [data],
    #     }
    # )


@router.post("/api/get_news_from_elt")
async def get_news_from_elt(elt: elt, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    list_fields = [
        "source_favicon",
        "source_name",
        "source_host_name",
        "source_language",
        "source_publishing_country",
        "data:title",
        "data:content",
        "pub_date",
        "data:title_translate",
        "data:content_translate",
        "data:class_sacthai",
        "data:url",
        "id",
        "_id",
        "list_user_read",
    ]
    vital = ""
    bookmarks = ""
    if elt.groupType == "vital":
        vital = "1"
    elif elt.groupType == "bookmarks":
        bookmarks = "1"
        
    result_elt = get_news_from_newsletter_id__(
        user_id=user_id,
        list_id=elt.newList,
        type=elt.type,
        id_nguon_nhom_nguon=elt.id_nguon_nhom_nguon,
        page_number=elt.page_number,
        page_size=elt.page_size,
        start_date=elt.startDate,
        end_date=elt.endDate,
        sac_thai=elt.sentiment,
        language_source=elt.langs,
        news_letter_id=elt.newsletter_id,
        text_search=elt.search_Query,
        vital=vital,
        bookmarks=bookmarks,
        is_get_read_state=True,
        list_fields=list_fields,
    )

    limit_string = 270

    for record in result_elt:
        try:
            record["data:content"] = record["data:content"][0:limit_string]
            record["data:content_translate"] = record["data:content_translate"][
                0:limit_string
            ]
        except:
            pass

    return JSONResponse(
        {
            "success": True,
            "total_record": len(result_elt),
            "result": result_elt[
                (int(elt.page_number) - 1)
                * int(elt.page_size) : (int(elt.page_number))
                * int(elt.page_size)
            ],
        }
    )


@router.post("/api/view_time_line")
def view_time_line(elt: elt, authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    # print("aa", elt.search_Query)
    vital = ""
    bookmarks = ""
    if elt.groupType == "vital":
        vital = "1"
    elif elt.groupType == "bookmarks":
        bookmarks = "1"
    result_elt = job_controller.view_time_line(elt, user_id, vital, bookmarks)
    return JSONResponse(
        {
            "success": True,
            "total_record": len(result_elt),
            "result": result_elt[
                (int(elt.page_number) - 1)
                * int(elt.page_size) : (int(elt.page_number))
                * int(elt.page_size)
            ],
        }
    )


@router.post("/api/start_job/{pipeline_id}")
def start_job(pipeline_id: str):
    return JSONResponse(job_controller.start_job(pipeline_id))


@router.post("/api/start_all_jobs")
def start_all_jobs():  # Danh sách Pipeline Id phân tách nhau bởi dấu , (VD: 636b5322243dd7a386d65cbc,636b695bda1ea6210d1b397f)
    return JSONResponse(job_controller.start_all_jobs(None))


@router.post("/api/stop_job/{pipeline_id}")
def stop_job(pipeline_id: str):
    return JSONResponse(job_controller.stop_job(pipeline_id))


@router.post("/api/stop_all_jobs")
def stop_all_jobs():
    return JSONResponse(job_controller.stop_all_jobs(None))


@router.get("/api/get_news_from_id_source")
def get_news_from_id_source(
    id="",
    type="",
    page_number=1,
    page_size=5,
    start_date: str = None,
    end_date: str = None,
    sac_thai: str = None,
    language_source: str = None,
    text_search=None,
):
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
    if language_source:
        language_source_ = language_source.split(",")
        language_source = []
        for i in language_source_:
            language_source.append(i)
    return JSONResponse(
        job_controller.get_news_from_id_source(
            id,
            type,
            page_number,
            page_size,
            start_date,
            end_date,
            sac_thai,
            language_source,
            text_search,
        )
    )


@router.post("/api/run_only_job/{pipeline_id}")
def run_only_job(pipeline_id: str, mode_test=True):
    if str(mode_test) == "True" or str(mode_test) == "true":
        mode_test = True
    result = job_controller.run_only(pipeline_id, mode_test)
    return result


@router.post("/api/create_required_keyword}")
def create_required_keyword(newsletter_id: str):
    return JSONResponse(job_controller.create_required_keyword(newsletter_id))


def find_child(_id, list_id_find_child):
    list_id_find_child.append(str(_id))
    child_subjects, child_count = MongoRepository().get_many_d(
        collection_name="newsletter", filter_spec={"parent_id": _id}
    )
    if child_count == 0:
        return str(_id)
    tmp = []
    for child in child_subjects:
        tmp.append(find_child(ObjectId(child["_id"]), list_id_find_child))
    return {str(_id): tmp}


def process_date(start_date, end_date):
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
            + "T23:59:59Z"
        )
    except:
        pass

    # news_letter_list_id = news_letter_list_id.split(',')
    if start_date == None and end_date == None:
        end_date = datetime.now().strftime("%Y-%m-%d") + "T23:59:59Z"
        start_date = (datetime.now() - timedelta(days=30)).strftime(
            "%Y-%m-%d"
        ) + "T00:00:00Z"
    return start_date, end_date


def get_children_info(child_id_list):
    info_tree = []
    for news_letter_id in child_id_list:
        a = MongoRepository().get_one(
            collection_name="newsletter",
            filter_spec={"_id": news_letter_id},
            filter_other={"_id": 1, "title": 1, "parent_id": 1},
        )
        a["_id"] = str(a["_id"])
        try:
            a["parent_id"] = str(a["parent_id"])
        except:
            pass
        info_tree.append(a)
    return info_tree


def build_keyword_query(query, keywords):
    query = ""
    first_flat = 1
    try:
        for keyword in keywords:
            if first_flat == 1:
                first_flat = 0
                query += "("
            else:
                query += "| ("
            keyword_arr = keyword.split(",")

            for keyword in keyword_arr:
                query += "+" + '"' + keyword + '"'
            query += ")"
    except:
        pass
    return query


def build_language_keyword_query(query, lang, keywords):
    query = ""
    first_flat = 1
    try:
        for keyword in keywords[lang]["required_keyword"]:
            if first_flat == 1:
                first_flat = 0
                query += "("
            else:
                query += "| ("
            keyword_arr = [key.strip() for key in keyword.split(",")]

            for keyword in keyword_arr:
                if keyword != "":
                    query += "+" + '"' + keyword + '"'
            query += ")"
    except:
        pass
    try:
        exclude_arr = keywords[lang]["exclusion_keyword"].split(",")
        for key_exclude in exclude_arr:
            if key_exclude != "":
                query += "-" + '"' + key_exclude + '"'
    except:
        pass
    return query


def summarize_query_keyword(keywords, first_lang):
    query = ""
    for keyword in keywords:
        if keyword != "":
            if first_lang == 1:
                first_lang = 0
                query += "(" + keyword + ")"
    return query


@router.get("/api/get_event_from_newsletter_list_id")
def get_event_from_newsletter_list_id(
    page_number=1,
    page_size=30,
    start_date: str = None,
    end_date: str = None,
    sac_thai: str = None,
    language_source: str = None,
    news_letter_id: str = "",
    authorize: AuthJWT = Depends(),
    event_number=None,
):
    start_date, end_date = process_date(start_date, end_date)
    result = []
    # start_date = f"{start_date_tmp.day}-{start_date_tmp.month}-{start_date_tmp.year}T00:00:00Z"
    # xử lý newletter parent
    child_id_list = []
    tree = find_child(ObjectId(news_letter_id), child_id_list)
    infor_tree = []
    for news_letter_id in child_id_list:
        child_newsletter = MongoRepository().get_one(
            collection_name="newsletter",
            filter_spec={"_id": news_letter_id},
            # filter_other={"_id": 1, "title": 1, "parent_id": 1},
        )
        child_newsletter["_id"] = str(child_newsletter["_id"])

        if child_newsletter.get("parent_id"):
            child_newsletter["parent_id"] = str(child_newsletter["parent_id"])

        if child_newsletter.get("user_id"):
            child_newsletter["user_id"] = str(child_newsletter["user_id"])

        if child_newsletter.get("news_id") != None:
            ls = [str(news_id) for news_id in child_newsletter.get("news_id")]
            child_newsletter["news_id"] = ls

        infor_tree.append(child_newsletter)

        try:
            if news_letter_id != "" and news_letter_id != None:
                if news_letter_id != "" and child_newsletter["tag"] == "gio_tin":
                    list_id = []
                    if child_newsletter.get("news_id") != None:
                        ls = [
                            str(news_id) for news_id in child_newsletter.get("news_id")
                        ]
                    if ls == []:
                        return []

                if news_letter_id != "" and child_newsletter["tag"] != "gio_tin":
                    if child_newsletter["is_sample"]:
                        query = ""
                        query = build_keyword_query(
                            query, child_newsletter.get("required_keyword_extract")
                        )
                    else:
                        first_lang = 1
                        query = ""
                        ### vi
                        query_vi = build_language_keyword_query(
                            "", "keyword_vi", child_newsletter
                        )
                        ### cn
                        query_cn = build_language_keyword_query(
                            "", "keyword_cn", child_newsletter
                        )
                        ### cn
                        query_ru = build_language_keyword_query(
                            "", "keyword_ru", child_newsletter
                        )
                        ### en
                        query_en = build_language_keyword_query(
                            "", "keyword_en", child_newsletter
                        )

                        query = summarize_query_keyword(
                            [query_vi, query_cn, query_ru, query_en], first_lang
                        )
            if query == "":
                continue
            plt_size = event_number * 2 if event_number else 100

            pipeline_dtos = my_es.search_main(
                index_name="vosint",
                query=query,
                gte=start_date,
                lte=end_date,
                lang=language_source,
                sentiment=sac_thai,
                size=plt_size,
            )

            list_id = [i["_source"]["id"] for i in pipeline_dtos]
            events_filter = {}
            if end_date != None and start_date == None:
                events_filter["created_at"] = {"$lte": end_date}
            if start_date != None and end_date == None:
                events_filter["created_at"] = {"$gte": start_date}

            if start_date != None and end_date != None:
                events_filter["$and"] = [
                    {"created_at": {"$gte": start_date}},
                    {"created_at": {"$lte": end_date}},
                ]
            events_filter["new_list"] = {"$elemMatch": {"$in": list_id}}

            if event_number:
                event_paginate = {"skip": 0, "limit": int(event_number)}
            else:
                event_number = {"skip": 0, "limit": 5}
            events, _ = MongoRepository().get_many_d(
                collection_name="events",
                filter_spec=events_filter,
                pagination_spec=event_paginate,
                order_spec=["date_created-desc"],
            )
            # sk = []
            relevent_news_ids = []  # [event for event in events]
            for event in events:
                if event.get("new_list"):
                    tmp = [
                        ObjectId(news_id) for news_id in event.get("new_list").copy()
                    ]
                    relevent_news_ids.extend(tmp)

            news_relevents, _ = MongoRepository().find(
                "News",
                filter_spec={"_id": {"$in": relevent_news_ids}},
                projection={"data:title": 1, "data:url": 1, "_id": 1},
            )

            news_dict = {
                str(news["_id"]): {
                    "data:title": news["data:title"],
                    "data:url": news["data:url"],
                }
                for news in news_relevents
            }

            for event in events:
                event["date_created"] = str(event.get("date_created"))
                event["_id"] = str(event.get("_id"))
                if event.get("new_list"):
                    tmp = []
                    for news_id in event.get("new_list"):
                        tmp.append(news_dict.get(news_id))
                    event["new_list"] = tmp.copy()
            result.append({news_letter_id: events.copy()})
        except Exception as e:
            print(e)
            pass
    # return result[(int(page_number)-1)*int(page_size):(int(page_number))*int(page_size)]
    return JSONResponse(
        {
            "success": True,
            "tree": tree,
            "infor_tree": infor_tree,
            "result": result[
                (int(page_number) - 1)
                * int(page_size) : (int(page_number))
                * int(page_size)
            ],
        }
    )


@router.get("/api/get_news_from_newsletter_id")
def get_news_from_newsletter_id(
    page_number=1,
    page_size=30,
    start_date: str = None,
    end_date: str = None,
    sac_thai: str = None,
    language_source: str = None,
    news_letter_id: str = "",
    authorize: AuthJWT = Depends(),
    text_search=None,
    vital: str = "",
    bookmarks: str = "",
):
    list_id = None
    query = None
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
    if language_source:
        language_source_ = language_source.split(",")
        language_source = []
        for i in language_source_:
            language_source.append(i)

    if vital == "1":
        authorize.jwt_required()
        user_id = authorize.get_jwt_subject()
        mongo = MongoRepository().get_one(
            collection_name="users", filter_spec={"_id": user_id}
        )
        ls = []
        try:
            for new_id in mongo["vital_list"]:
                ls.append(str(new_id))
        except:
            pass
        if ls == []:
            return []
        list_id = ls

    elif bookmarks == "1":
        authorize.jwt_required()
        user_id = authorize.get_jwt_subject()
        mongo = MongoRepository().get_one(
            collection_name="users", filter_spec={"_id": user_id}
        )
        ls = []
        kt_rong = 1
        try:
            for new_id in mongo["news_bookmarks"]:
                ls.append(str(new_id))
        except:
            pass
        if ls == []:
            return []
        list_id = ls

    a = MongoRepository().get_one(
        collection_name="newsletter", filter_spec={"_id": news_letter_id}
    )

    if news_letter_id != "" and a["tag"] == "gio_tin":
        ls = []
        kt_rong = 1
        try:
            for new_id in a["news_id"]:
                ls.append(str(new_id))
        except:
            pass
        if ls == []:
            return []
        list_id = ls

    
    if news_letter_id != "" and a["tag"] != "gio_tin":
        if a["is_sample"]:
            query = ""
            first_flat = 1
            try:
                for i in a["required_keyword_extract"]:
                    if first_flat == 1:
                        first_flat = 0
                        query += "("
                    else:
                        query += "| ("
                    j = i.split(",")

                    for k in j:
                        query += "+" + '"' + k + '"'
                    query += ")"
            except:
                pass
        else:
            first_lang = 1
            query = ""
            ### vi
            query_vi = ""
            first_flat = 1
            try:
                for i in a["keyword_vi"]["required_keyword"]:
                    if first_flat == 1:
                        first_flat = 0
                        query_vi += "("
                    else:
                        query_vi += "| ("
                    j = i.split(",")

                    for k in j:
                        query_vi += "+" + '"' + k + '"'
                    query_vi += ")"
            except:
                pass
            try:
                j = a["keyword_vi"]["exclusion_keyword"].split(",")
                for k in j:
                    query_vi += "-" + '"' + k + '"'
            except:
                pass

            ### cn
            query_cn = ""
            first_flat = 1
            try:
                for i in a["keyword_vn"]["required_keyword"]:
                    if first_flat == 1:
                        first_flat = 0
                        query_cn += "("
                    else:
                        query_cn += "| ("
                    j = i.split(",")

                    for k in j:
                        query_cn += "+" + '"' + k + '"'
                    query_cn += ")"
            except:
                pass
            try:
                j = a["keyword_cn"]["exclusion_keyword"].split(",")
                for k in j:
                    query_cn += "-" + '"' + k + '"'
            except:
                pass

            ### cn
            query_ru = ""
            first_flat = 1
            try:
                for i in a["keyword_ru"]["required_keyword"]:
                    if first_flat == 1:
                        first_flat = 0
                        query_ru += "("
                    else:
                        query_ru += "| ("
                    j = i.split(",")

                    for k in j:
                        query_ru += "+" + '"' + k + '"'
                    query_ru += ")"
            except:
                pass
            try:
                j = a["keyword_ru"]["exclusion_keyword"].split(",")
                for k in j:
                    query_ru += "-" + '"' + k + '"'
            except:
                pass

            ### cn
            query_en = ""
            first_flat = 1
            try:
                for i in a["keyword_en"]["required_keyword"]:
                    if first_flat == 1:
                        first_flat = 0
                        query_en += "("
                    else:
                        query_en += "| ("
                    j = i.split(",")

                    for k in j:
                        query_en += "+" + '"' + k + '"'
                    query_en += ")"
            except:
                pass
            try:
                j = a["keyword_en"]["exclusion_keyword"].split(",")
                for k in j:
                    query_en += "-" + '"' + k + '"'
            except:
                pass

            if query_vi != "":
                if first_lang == 1:
                    first_lang = 0
                    query += "(" + query_vi + ")"
            if query_en != "":
                if first_lang == 1:
                    first_lang = 0
                    query += "(" + query_en + ")"
                else:
                    query += "| (" + query_en + ")"
            if query_ru != "":
                if first_lang == 1:
                    first_lang = 0
                    query += "(" + query_ru + ")"
                else:
                    query += "| (" + query_ru + ")"
            if query_cn != "":
                if first_lang == 1:
                    first_lang = 0
                    query += "(" + query_cn + ")"
                else:
                    query += "| (" + query_cn + ")"

    # if text_search != None and news_letter_id != None:
    #     query += '+(' + text_search + ')'
    # elif text_search != None:
    #     query = ''
    #     query += ' AND (' + text_search + ')'
    if text_search == None:
        pipeline_dtos = my_es.search_main(
            index_name="vosint",
            query=query,
            gte=start_date,
            lte=end_date,
            lang=language_source,
            sentiment=sac_thai,
            list_id=list_id,
        )
    else:
        pipeline_dtos = my_es.search_main(
            index_name="vosint",
            query=query,
            gte=start_date,
            lte=end_date,
            lang=language_source,
            sentiment=sac_thai,
            list_id=list_id,
        )
        list_id = []
        for i in range(len(pipeline_dtos)):
            list_id.append(pipeline_dtos[i]["_source"]["id"])
        pipeline_dtos = my_es.search_main(
            index_name="vosint",
            query=text_search,
            gte=start_date,
            lte=end_date,
            lang=language_source,
            sentiment=sac_thai,
            list_id=list_id,
        )
    # list_link = []
    # for i in pipeline_dtos:
    #     list_link.append({"data:url":i['_source']['url']})

    # a,_ = MongoRepository().get_many_d(collection_name='News',filter_spec={'$or': list_link.copy()}, filter_other={"_id":1})
    # list_id = []
    # for i in a:
    #     list_id.append(str(i['_id']))

    # a,_ = MongoRepository().get_many_d(collection_name='event')

    # result = []
    # for i in a:
    #     kt = 0
    #     try:
    #         for j in i['new_list']:
    #             print(j)
    #             if j in list_id:
    #                 i['_id']=str(i['_id'])
    #                 result.append(i)
    #                 kt = 1
    #             if kt == 1:
    #                 continue
    #         if kt == 1:
    #             continue
    #     except:
    #         pass
    for i in range(len(pipeline_dtos)):
        try:
            pipeline_dtos[i]["_source"]["_id"] = pipeline_dtos[i]["_source"]["id"]
        except:
            pass
        pipeline_dtos[i] = pipeline_dtos[i]["_source"].copy()

    return JSONResponse(
        {
            "success": True,
            "total_record": len(pipeline_dtos),
            "result": pipeline_dtos[
                (int(page_number) - 1)
                * int(page_size) : (int(page_number))
                * int(page_size)
            ],
        }
    )


@router.get("/api/get_result_job/News_search")
def News_search(
    text_search="*",
    page_number=1,
    page_size=30,
    start_date: str = None,
    end_date: str = None,
    sac_thai: str = None,
    language_source: str = None,
    news_letter_id: str = "",
    authorize: AuthJWT = Depends(),
    vital: str = "",
    bookmarks: str = "",
):
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
    # print(start_date)
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
    # print(end_date)
    pipeline_dtos = my_es.search_main(
        index_name="vosint",
        query=text_search,
        gte=start_date,
        lte=end_date,
        lang=language_source,
        sentiment=sac_thai,
    )

    return JSONResponse(
        {
            "success": True,
            "result": pipeline_dtos[
                (int(page_number) - 1)
                * int(page_size) : (int(page_number))
                * int(page_size)
            ],
        }
    )


@router.get("/api/get_result_job/News")
def get_result_job(
    order=None,
    text_search="",
    page_number=None,
    page_size=None,
    start_date: str = "",
    end_date: str = "",
    sac_thai: str = "",
    language_source: str = "",
    news_letter_id: str = "",
    authorize: AuthJWT = Depends(),
    vital: str = "",
    bookmarks: str = "",
):
    authorize.jwt_required()
    user_id = authorize.get_jwt_subject()
    # print(user_id)
    try:
        query = {}
        query["$and"] = []

        if start_date != "" and end_date != "":
            if text_search != "":
                start_date = (
                    start_date.split("/")[2]
                    + "-"
                    + start_date.split("/")[1]
                    + "-"
                    + start_date.split("/")[0]
                    + "T00:00:00Z"
                )
                end_date = (
                    end_date.split("/")[2]
                    + "-"
                    + end_date.split("/")[1]
                    + "-"
                    + end_date.split("/")[0]
                    + "T00:00:00Z"
                )

            if text_search == None or text_search == "":
                start_date = datetime(
                    int(start_date.split("/")[2]),
                    int(start_date.split("/")[1]),
                    int(start_date.split("/")[0]),
                )
                end_date = datetime(
                    int(end_date.split("/")[2]),
                    int(end_date.split("/")[1]),
                    int(end_date.split("/")[0]),
                )

                query["$and"].append(
                    {"pub_date": {"$gte": start_date, "$lte": end_date}}
                )
        elif start_date != "":
            if text_search != "":
                start_date = (
                    start_date.split("/")[2]
                    + "-"
                    + start_date.split("/")[1]
                    + "-"
                    + start_date.split("/")[0]
                    + "T00:00:00Z"
                )

            if text_search == None or text_search == "":
                start_date = datetime(
                    int(start_date.split("/")[2]),
                    int(start_date.split("/")[1]),
                    int(start_date.split("/")[0]),
                )
                query["$and"].append({"pub_date": {"$gte": start_date}})
        elif end_date != "":
            if text_search != "":
                end_date = (
                    end_date.split("/")[2]
                    + "-"
                    + end_date.split("/")[1]
                    + "-"
                    + end_date.split("/")[0]
                    + "T00:00:00Z"
                )
            if text_search == None or text_search == "":
                end_date = datetime(
                    int(end_date.split("/")[2]),
                    int(end_date.split("/")[1]),
                    int(end_date.split("/")[0]),
                )
                query["$and"].append({"pub_date": {"$lte": end_date}})
        if sac_thai != "" and sac_thai != "all":
            query["$and"].append({"data:class_sacthai": sac_thai})
        if language_source != "":
            language_source_ = language_source.split(",")
            language_source = []
            for i in language_source_:
                language_source.append(i)
            ls = []
            for i in language_source:
                ls.append({"source_language": i})

            query["$and"].append({"$or": ls.copy()})
        if news_letter_id != "":
            mongo = MongoRepository().get_one(
                collection_name="newsletter", filter_spec={"_id": news_letter_id}
            )
            ls = []
            kt_rong = 1
            try:
                for new_id in mongo["news_id"]:
                    ls.append({"_id": new_id})
                    kt_rong = 0
                if kt_rong == 0:
                    query["$and"].append({"$or": ls.copy()})
            except:
                if kt_rong == 1:
                    query["$and"].append(
                        {"khong_lay_gi": "bggsjdgsjgdjádjkgadgưđạgjágdjágdjkgạdgágdjka"}
                    )
        elif vital == "1":
            mongo = MongoRepository().get_one(
                collection_name="users", filter_spec={"_id": user_id}
            )
            ls = []
            kt_rong = 1
            try:
                for new_id in mongo["vital_list"]:
                    ls.append({"_id": new_id})
                    kt_rong = 0
                if kt_rong == 0:
                    query["$and"].append({"$or": ls.copy()})
            except:
                if kt_rong == 1:
                    query["$and"].append(
                        {"khong_lay_gi": "bggsjdgsjgdjádjkgadgưđạgjágdjágdjkgạdgágdjka"}
                    )
        elif bookmarks == "1":
            mongo = MongoRepository().get_one(
                collection_name="users", filter_spec={"_id": user_id}
            )
            ls = []
            kt_rong = 1
            try:
                for new_id in mongo["news_bookmarks"]:
                    ls.append({"_id": new_id})
                    kt_rong = 0
                if kt_rong == 0:
                    query["$and"].append({"$or": ls.copy()})
            except:
                if kt_rong == 1:
                    query["$and"].append(
                        {"khong_lay_gi": "bggsjdgsjgdjádjkgadgưđạgjágdjágdjkgạdgágdjka"}
                    )
        elif text_search != "":
            # tmp = my_es.search_main(index_name="vosint", query=text_search)
            # # print(text_search)
            # # print(tmp)
            # list_link = []
            # for k in tmp:
            #     list_link.append({"data:url": k["_source"]["data:url"]})
            # if len(list_link) != 0:
            #     query["$and"].append({"$or": list_link.copy()})
            # else:
            #     query["$and"].append(
            #         {"khong_lay_gi": "bggsjdgsjgdjádjkgadgưđạgjágdjágdjkgạdgágdjka"}
            #     )

            pipeline_dtos = my_es.search_main(
                index_name="vosint",
                query=text_search,
                gte=start_date,
                lte=end_date,
                lang=language_source,
                sentiment=sac_thai,
                size=(int(page_number)) * int(page_size),
            )

            total_record = len(pipeline_dtos)
            for i in range(len(pipeline_dtos)):
                try:
                    pipeline_dtos[i]["_source"]["_id"] = pipeline_dtos[i]["_source"][
                        "id"
                    ]
                except:
                    pass
                pipeline_dtos[i] = pipeline_dtos[i]["_source"].copy()

            news_ids = [ObjectId(row["id"]) for row in pipeline_dtos]
            raw_isreads, _ = MongoRepository().get_many(
                "News", {"_id": {"$in": news_ids}}
            )
            isread = {}
            for raw_isread in raw_isreads:
                isread[str(raw_isread["_id"])] = raw_isread.get("list_user_read")
            for row in pipeline_dtos:
                row["list_user_read"] = isread.get(row["_id"])

            result = pipeline_dtos[
                (int(page_number) - 1)
                * int(page_size) : (int(page_number))
                * int(page_size)
            ]
            # return {"result": result, "total_record": len(pipeline_dtos)}

            # query["$and"].append(
            #     {
            #         "$or": [
            #             {
            #                 "data:title": {
            #                     # "$regex": rf"\b{text_search}\b",
            #                     # "$options": "i",
            #                     # "$regex": text_search,
            #                     "$regex": rf"(?<![\p{{L}}\p{{N}}]){re.escape(text_search.strip())}(?![\p{{L}}\p{{N}}])",
            #                     "$options": "iu",
            #                 }
            #             },
            #             {
            #                 "data:content": {
            #                     # "$regex": rf"\b{text_search}\b",
            #                     # "$options": "i",
            #                     # "$regex": text_search,
            #                     "$regex": rf"(?<![\p{{L}}\p{{N}}]){re.escape(text_search.strip())}(?![\p{{L}}\p{{N}}])",
            #                     "$options": "iu",
            #                 }
            #             },
            #         ]
            #     },
            # )
    except:
        query = {}
    if str(query) == "{'$and': []}":
        query = {}

    # order="data: gtitle"
    if text_search == None or text_search == "":
        result = job_controller.get_result_job(
            "News", order, page_number, page_size, filter=query
        )

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

    current_result = (
        result["result"] if (text_search == None or text_search == "") else result
    )
    for record in current_result:
        try:
            record["data:content"] = record["data:content"][0:limit_string]
            record["data:content_translate"] = record["data:content_translate"][
                0:limit_string
            ]
        except:
            pass
        for key in list_fields:
            record.pop(key, None)

    return (
        result
        if (text_search == None or text_search == "")
        else {"result": result, "total_record": total_record}
    )

    # return JSONResponse(
    #     job_controller.get_result_job(
    #         "News", order, page_number, page_size, filter=query
    #     )
    # )


@router.get("/api/get_table")
def get_table(
    name,
    id=None,
    order=None,
    page_number=None,
    page_size=None,
    text_search="",
    start_date="",
    end_date="",
    sac_thai="",
    # language_source="",
):
    query = {}
    query["$and"] = []

    if id != None:
        query["id"] = str(id)

    # filter by start_date, end_date, text_search
    if start_date != "" and end_date != "":
        start_date = datetime(
            int(start_date.split("/")[2]),
            int(start_date.split("/")[1]),
            int(start_date.split("/")[0]),
        )
        end_date = datetime(
            int(end_date.split("/")[2]),
            int(end_date.split("/")[1]),
            int(end_date.split("/")[0]),
        )

        end_date = end_date.replace(hour=23, minute=59, second=59)

        start_date = str(start_date).replace("-", "/")
        end_date = str(end_date).replace("-", "/")
        query["$and"].append({"created_at": {"$gte": start_date, "$lte": end_date}})

    elif start_date != "":
        start_date = datetime(
            int(start_date.split("/")[2]),
            int(start_date.split("/")[1]),
            int(start_date.split("/")[0]),
        )
        start_date = str(start_date).replace("-", "/")
        query["$and"].append({"created_at": {"$gte": start_date}})

    elif end_date != "":
        end_date = datetime(
            int(end_date.split("/")[2]),
            int(end_date.split("/")[1]),
            int(end_date.split("/")[0]),
        )
        end_date = str(end_date).replace("-", "/")
        query["$and"].append({"created_at": {"$lte": end_date}})

    if sac_thai != "" and sac_thai != "all":
        query["$and"].append({"sentiment": sac_thai})

    if text_search != "":
        query["$and"].append(
            {
                "$or": [
                    {"header": {"$regex": text_search, "$options": "i"}},
                    {"content": {"$regex": text_search, "$options": "i"}},
                ]
            }
        )

    if str(query) == "{'$and': []}":
        query = {}

    # limit_string = 270

    # result = job_controller.get_result_job(
    #     name, order, page_number, page_size, filter=query
    # )

    # list_fields = [
    #     "id_data_ft",
    #     "footer_date",
    #     "footer_type",
    #     "video_id",
    #     "video_link",
    #     "post_link",
    #     "post_id",
    #     "user_id",
    # ]

    # for record in result["result"]:
    #     try:
    #         record["content"] = record["content"][0:limit_string]
    #     except:
    #         pass
    #     for key in list_fields:
    #         record.pop(key, None)

    # return result

    return JSONResponse(
        job_controller.get_result_job(name, order, page_number, page_size, filter=query)
    )


@router.get("/api/test/{pipeline_id}")
def get_result_job(pipeline_id):
    return JSONResponse(job_controller.test_only(pipeline_id))


@router.get("/api/get_log_history/{pipeline_id}")
def get_log_history(pipeline_id: str, order=None, page_number=None, page_size=None):
    return JSONResponse(
        job_controller.get_log_history(pipeline_id, order, page_number, page_size)
    )


@router.get("/api/get_log_history_last/{pipeline_id}")
def get_log_history(pipeline_id: str):
    try:
        return JSONResponse(
            job_controller.get_log_history_last(pipeline_id)["result"][-1]
        )
    except:
        return JSONResponse(job_controller.get_log_history_last(pipeline_id)["result"])


@router.get("/api/get_log_history_error_or_getnews/{pipeline_id}")
def get_log_history_error_or_getnews(
    pipeline_id: str,
    order=None,
    page_number=None,
    page_size=None,
    start_date: str = None,
    end_date: str = None,
):
    job_controller_v2 = JobController()
    return JSONResponse(
        job_controller_v2.get_log_history_error_or_getnews(
            pipeline_id, order, page_number, page_size, start_date, end_date
        )
    )


@router.post("/search_news_from_object")
def search_news_from_object(
    page_number=1,
    page_size=30,
    start_date: str = None,
    end_date: str = None,
    sac_thai: str = None,
    language_source: str = None,
    text_search=None,
    object_id=None,
):
    # try:
    #     start_date = (
    #         start_date.split("/")[2]
    #         + "-"
    #         + start_date.split("/")[1]
    #         + "-"
    #         + start_date.split("/")[0]
    #         + "T00:00:00Z"
    #     )
    # except:
    #     pass
    # try:
    #     end_date = (
    #         end_date.split("/")[2]
    #         + "-"
    #         + end_date.split("/")[1]
    #         + "-"
    #         + end_date.split("/")[0]
    #         + "T00:00:00Z"
    #     )
    # except:
    #     pass

    data = job_controller.search_news_by_object(
        page_number,
        page_size,
        start_date,
        end_date,
        sac_thai,
        language_source,
        text_search,
        object_id,
    )
    return JSONResponse(data, status_code=200)


@router.post("/api/get_table_ttxvn")
async def get_table_ttxvn(
    name,
    order=None,
    page_number=None,
    page_size=None,
    crawling: str = None,
    text_search: str = None,
    start_date="",
    end_date="",
):
    query = {}
    query["$and"] = []
    if start_date != "" and end_date != "":
        start_date = datetime(
            int(start_date.split("/")[2]),
            int(start_date.split("/")[1]),
            int(start_date.split("/")[0]),
        )
        end_date = datetime(
            int(end_date.split("/")[2]),
            int(end_date.split("/")[1]),
            int(end_date.split("/")[0]),
        )

        end_date = end_date.replace(hour=23, minute=59, second=59)

        query["$and"].append({"PublishDate": {"$gte": start_date, "$lte": end_date}})
    elif start_date != "":
        start_date = datetime(
            int(start_date.split("/")[2]),
            int(start_date.split("/")[1]),
            int(start_date.split("/")[0]),
        )
        query["$and"].append({"PublishDate": {"$gte": start_date}})
    elif end_date != "":
        end_date = datetime(
            int(end_date.split("/")[2]),
            int(end_date.split("/")[1]),
            int(end_date.split("/")[0]),
        )
        end_date = end_date.replace(hour=23, minute=59, second=59)

        query["$and"].append({"PublishDate": {"$lte": end_date}})
    if text_search != None and text_search != "":
        query["$and"].append({"Title": {"$regex": str(text_search), "$options": "i"}})
    if crawling != None:
        if crawling == "crawled":
            query["$and"].append({"content": {"$exists": True, "$ne": "", "$ne": None}})
        elif crawling == "not_crawled":
            query["$and"].append(
                {
                    "$or": [
                        {"content": {"$exists": False}},
                        {"content": None},
                        {"content": ""},
                    ]
                }
            )
    if query["$and"] == []:
        query = {}

    data = job_controller.get_result_job(
        name, order, page_number, page_size, filter=query
    )

    for row in data.get("result"):
        row["PublishDate"] = str(row.get("PublishDate"))
        row["Created"] = str(row.get("Created"))

    return JSONResponse(data)


@router.get("/get-total-crawl")
async def get_total_crawl(current_date: str):
    # current_date = datetime.utcnow().strftime("%d/%m/%Y")

    start_date = datetime(
        int(current_date.split("/")[2]),
        int(current_date.split("/")[1]),
        int(current_date.split("/")[0]),
    )

    end_date = datetime(
        int(current_date.split("/")[2]),
        int(current_date.split("/")[1]),
        int(current_date.split("/")[0]),
    )

    end_date = end_date.replace(hour=23, minute=59, second=59)

    filter_spec = {
        "$and": [
            {"PublishDate": {"$gte": start_date}},
            {"PublishDate": {"$lte": end_date}},
            {"content": {"$exists": True}},
            {"content": {"$ne": ""}},
            {"content": {"$ne": None}},
        ]
    }
    total = 0

    total = await ttxvn_client.count_documents(filter_spec)
    return total


@router.post("/api/translate")
def translate(data: Translate):
    result = job_controller.translate(data.lang, data.content)
    return JSONResponse({"results": result})


@router.post("/api/crawling_ttxvn")
def crawling_ttxvn(job_ids: List[str]):
    # req = requests.post(settings.PIPELINE_API, params={"job_id": job_id})
    # req = requests.post(
    #     "http://192.168.1.11:3101/Job/api/crawling_ttxvn", params={"job_id": job_id}
    # )
    req = requests.post(
        f"{settings.PIPELINE_API}/Job/api/crawling_ttxvn", data=json.dumps(job_ids)
    )

    if req.ok:
        return JSONResponse(req.json())
    return JSONResponse({"succes": "False"})


@router.get("/api/get_history_statistic_by_id")
def get_history_statistic_by_id(
    pipeline_id: str, n_days: int = 7, start_date: str = None, end_date: str = None
):
    return job_controller.get_history_statistic_by_id(
        pipeline_id, start_date, end_date, n_days
    )
