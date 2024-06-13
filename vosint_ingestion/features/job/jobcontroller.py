from .services import JobService
from vosint_ingestion.features.job.services.get_news_from_elastic import (
    get_news_from_newsletter_id__,
)
from bson.objectid import ObjectId
from models import MongoRepository
import requests
from core.config import settings
import json
from datetime import datetime
import re
from vosint_ingestion.features.minh.Elasticsearch_main.elastic_main import (
    My_ElasticSearch,
)
from vosint_ingestion.features.job.services.get_news_from_elastic import build_keyword, combine_keyword

news_es = My_ElasticSearch()


def get_depth(mylist):
    if isinstance(mylist, list):
        return 1 + max(get_depth(item) for item in mylist)
    else:
        return 0


class JobController:
    def __init__(self):
        self.__job_service = JobService()

    def start_job(self, pipeline_id: str):
        self.__job_service.start_job(pipeline_id)

        return {"success": True}

    def start_all_jobs(self, pipeline_ids=None):
        # Receives request data
        # pipeline_ids = request.args.get('pipeline_ids')

        self.__job_service.start_all_jobs(pipeline_ids)

        return {"success": True}

    def stop_job(self, pipeline_id: str):
        self.__job_service.stop_job(pipeline_id)

        return {"success": True}

    def stop_all_jobs(self, pipeline_ids):
        # Receives request data
        # pipeline_ids = request.args.get('pipeline_ids')

        self.__job_service.stop_all_jobs(pipeline_ids)
        return {"success": True}

    ### Doan
    def get_news_from_id_source(
        self,
        id,
        type,
        page_number,
        page_size,
        start_date,
        end_date,
        sac_thai,
        language_source,
        text_search,
    ):
        page_number = int(page_number)
        page_size = int(page_size)
        result = self.__job_service.get_news_from_id_source(
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
        return {
            "total_record": len(result),
            "result": result[
                (int(page_number) - 1)
                * int(page_size) : (int(page_number))
                * int(page_size)
            ],
        }

    def create_required_keyword(self, newsletter_id):
        try:
            self.__job_service.create_required_keyword(newsletter_id)
            return {"success": True}
        except:
            return {"success": True}

    def run_only(self, pipeline_id: str, mode_test):
        result = self.__job_service.run_only(pipeline_id, mode_test)
        return result

    def get_result_job(self, News, order, page_number, page_size, filter):
        # Receives request data
        # order = request.args.get('order')
        # order = request.args.get('order')
        # page_number = request.args.get('page_number')
        page_number = int(page_number) if page_number is not None else None
        # page_size = request.args.get('page_size')
        page_size = int(page_size) if page_size is not None else None

        # Create sort condition
        order_spec = order.split(",") if order else []

        # Calculate pagination information
        page_number = page_number if page_number else 1
        page_size = page_size if page_size else 20
        pagination_spec = {"skip": page_size * (page_number - 1), "limit": page_size}

        (
            pipeline_dtos,
            total_records,
        ) = self.__job_service.get_result_job(
            News, order_spec=order_spec, pagination_spec=pagination_spec, filter=filter
        )

        for i in pipeline_dtos:
            try:
                i["_id"] = str(i["_id"])
            except:
                pass
            try:
                i["pub_date"] = str(i.get("pub_date"))
                i["created"] = str(i.get("created"))
                i["id_social"] = str(i.get("id_social"))
            except:
                pass
        return {
            "success": True,
            "total_record": total_records,
            "result": pipeline_dtos,
        }

    def run_one_foreach(self, pipeline_id: str):
        result = self.__job_service.run_one_foreach(pipeline_id)

        return {"result": str(result)}

    def test_only(self, pipeline_id: str):
        result = self.__job_service.test_only(pipeline_id)

        return result

    def get_log_history(self, pipeline_id: str, order, page_number, page_size):
        # Receives request data
        # order = request.args.get('order')
        # order = request.args.get('order')
        # page_number = request.args.get('page_number')
        page_number = int(page_number) if page_number is not None else None
        # page_size = request.args.get('page_size')
        page_size = int(page_size) if page_size is not None else None

        # Create sort condition
        order_spec = order.split(",") if order else []

        # Calculate pagination information
        page_number = page_number if page_number else 1
        page_size = page_size if page_size else 20
        pagination_spec = {"skip": page_size * (page_number - 1), "limit": page_size}

        result = self.__job_service.get_log_history(
            pipeline_id, order_spec=order_spec, pagination_spec=pagination_spec
        )

        return {"success": True, "total_record": result[1], "result": result[0]}

    def get_log_history_last(self, pipeline_id: str):
        result = self.__job_service.get_log_history_last(pipeline_id)

        return {"success": True, "total_record": result[1], "result": result[0]}

    def get_log_history_error_or_getnews(
        self, pipeline_id: str, order, page_number, page_size, start_date, end_date
    ):
        if start_date is not None and start_date != "":
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
        if end_date is not None and end_date != "":
            end_date = datetime.strptime(end_date, "%d/%m/%Y")
        # Receives request data
        # order = request.args.get('order')
        # order = request.args.get('order')
        # page_number = request.args.get('page_number')
        page_number = int(page_number) if page_number is not None else None
        # page_size = request.args.get('page_size')
        page_size = int(page_size) if page_size is not None else None

        # Create sort condition
        order_spec = order.split(",") if order else []

        # Calculate pagination information
        page_number = page_number if page_number else 1
        page_size = page_size if page_size else 20
        pagination_spec = {"skip": page_size * (page_number - 1), "limit": page_size}

        result = self.__job_service.get_log_history_error_or_getnews(
            pipeline_id,
            order_spec=order_spec,
            pagination_spec=pagination_spec,
            start_date=start_date,
            end_date=end_date,
        )

        return {"success": True, "total_record": result[1], "result": result[0]}

    def elt_search(
        self,
        page_number,
        page_size,
        start_date,
        end_date,
        sac_thai,
        language_source,
        text_search,
        ids,
    ):
        pipeline_dtos = self.__job_service.elt_search(
            start_date, end_date, sac_thai, language_source, text_search, ids
        )
        for i in range(len(pipeline_dtos)):
            try:
                pipeline_dtos[i]["_source"]["_id"] = pipeline_dtos[i]["_source"]["id"]
            except:
                pass
            pipeline_dtos[i] = pipeline_dtos[i]["_source"].copy()
        return {
            "total_record": len(pipeline_dtos),
            "result": pipeline_dtos[
                (int(page_number) - 1)
                * int(page_size) : (int(page_number))
                * int(page_size)
            ],
        }

    def view_time_line(
        self,
        elt,
        user_id,
        vital,
        bookmarks,
    ):
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
        )
        ids = [x["id"] for x in result_elt]

        filter_spec = {}
        filter_spec.update({"new_list": {"$in": ids}})

        if elt.endDate != None and elt.endDate != "":
            _end_date = datetime.strptime(elt.endDate, "%d/%m/%Y")
            filter_spec.update({"date_created": {"$lte": _end_date}})
        if elt.startDate != None and elt.startDate != "":
            _start_date = datetime.strptime(elt.startDate, "%d/%m/%Y")

            if filter_spec.get("date_created") == None:
                filter_spec.update({"date_created": {"$gte": _start_date}})
            else:
                filter_spec["date_created"].update({"$gte": _start_date})

        timelines, _ = MongoRepository().get_many(
            "events",
            filter_spec,
            ["date_created"],
        )
        for timeline in timelines:
            timeline["_id"] = str(timeline["_id"])
            timeline["date_created"] = str(timeline["date_created"])
        return timelines

    
    def search_news_by_object(
        self,
        page_number,
        page_size,
        start_date,
        end_date,
        sac_thai,
        language_source,
        text_search,
        object_id,
    ):
        filter_spec = {}
        sentiment_label = {
            "1": "positive",
            "2": "negative",
            "0": "normal"
        }
        
        sentiment_statistic = {
            "all": 0,
            "positive": 0,
            "negative": 0,
            "normal": 0
        }
        if text_search != None and text_search != "":
            filter_spec.update(
                {
                    "$or": [
                        {
                            "data:content": {
                                "$regex": rf"(?<![\p{{L}}\p{{N}}]){re.escape(text_search.strip())}(?![\p{{L}}\p{{N}}])",
                                "$options": "iu",
                            }
                        },
                        {
                            "data:title": {
                                "$regex": rf"(?<![\p{{L}}\p{{N}}]){re.escape(text_search.strip())}(?![\p{{L}}\p{{N}}])",
                                "$options": "iu",
                            }
                        },
                    ]
                },
            )

        if end_date != None and end_date != "":
            _end_date = datetime.strptime(end_date, "%d/%m/%Y")
            filter_spec.update({"pub_date": {"$lte": _end_date}})
            if text_search != "" or text_search != None:
                end_date = (
                    end_date.split("/")[2]
                    + "-"
                    + end_date.split("/")[1]
                    + "-"
                    + end_date.split("/")[0]
                    + "T00:00:00Z"
                )
        if start_date != None and start_date != "":
            _start_date = datetime.strptime(start_date, "%d/%m/%Y")
            if filter_spec.get("pub_date") == None:
                filter_spec.update({"pub_date": {"$gte": _start_date}})
            else:
                filter_spec["pub_date"].update({"$gte": _start_date})
            if text_search != "" or text_search != None:
                start_date = (
                    start_date.split("/")[2]
                    + "-"
                    + start_date.split("/")[1]
                    + "-"
                    + start_date.split("/")[0]
                    + "T00:00:00Z"
                )

        if sac_thai != None and sac_thai != "":
            filter_spec.update({"data:class_sacthai": sac_thai})
        if language_source != None and language_source != "":
            language_source_ = language_source.split(",")
            language_source = []
            for i in language_source_:
                language_source.append(i)
            ls = []
            for i in language_source:
                ls.append(i)

            filter_spec.update({"source_language": {"$in": ls.copy()}})

        try:
            
            objects, _ = MongoRepository().find("object", {"_id": ObjectId(object_id)}, {"keywords": 1, "news_list":1})

            if len(objects) == 0:
                return {"sentiments": {}, "result": [], "total_record": 0}
            
            news_ids = (
                [ObjectId(news_id) for news_id in objects[0].get("news_list")]
                if (text_search == "" or text_search == None)
                else [news_id for news_id in objects[0].get("news_list")]
            )

            total = len(objects[0].get("news_list"))
            filter_spec["_id"] = {"$in": news_ids}

            if text_search == "" or text_search == None:
                page_number = int(page_number) if page_number is not None else None
                page_size = int(page_size) if page_size is not None else None
                page_number = page_number if page_number else 1
                page_size = page_size if page_size else 20
                pagination_spec = {
                    "skip": page_size * (page_number - 1),
                    "limit": page_size,
                }
                news, _ = MongoRepository().get_many_News(
                    "News", filter_spec, ["pub_date"], pagination_spec=pagination_spec
                )
                sentiment_pipeline = [
                                        {"$match": filter_spec}, 
                                        {
                                            '$group': {
                                                '_id': '$data:class_sacthai', 
                                                'count': {
                                                    '$sum': 1
                                                }
                                            }  
                                        }
                                    ]
                sentiment_count, _ = MongoRepository().aggregate("News",sentiment_pipeline)
                sentiment_statistic = {sentiment_label[x["_id"]]:x["count"] for x in sentiment_count}
                sentiment_statistic["all"] = sum(list(sentiment_statistic.values()))
                
                for row_new in news:
                    row_new["_id"] = str(row_new["_id"])
                    row_new["pub_date"] = str(row_new["pub_date"])
            else:
                keyword_dict = objects[0].get("keywords") 
                query_vi, first_flat = build_keyword([keyword_dict.get("vi")], 1) 
                query_ru, first_flat = build_keyword([keyword_dict.get("ru")], first_flat)
                query_en, first_flat = build_keyword([keyword_dict.get("en")], first_flat)
                query_cn, first_flat = build_keyword([keyword_dict.get("cn")], first_flat)
                query = combine_keyword(query_vi, query_ru, query_en, query_cn)
                query = f'({query})+("{text_search}")'
                search_params = {
                    "index_name": "vosint",
                    "query": query,
                    "gte": start_date,
                    "lte": end_date,
                    "lang": language_source,
                    "sentiment": sac_thai,
                    "list_id": news_ids,
                    "size": int(page_number) * int(page_size)
                }
                pipeline_dtos = news_es.search_main(**search_params)
                #--count positive--
                search_params["sentiment"] = "1"
                sentiment_statistic["positive"] = news_es.count_search_main(**search_params)
                #--count negative--
                search_params["sentiment"] = "2"
                sentiment_statistic["negative"] = news_es.count_search_main(**search_params)
                #--count normal--
                search_params["sentiment"] = "0"
                sentiment_statistic["normal"] = news_es.count_search_main(**search_params)
                sentiment_statistic["all"] = sum(list(sentiment_statistic.values()))
                total = len(pipeline_dtos)

                for i in range(len(pipeline_dtos)):
                    try:
                        pipeline_dtos[i]["_source"]["_id"] = pipeline_dtos[i][
                            "_source"
                        ]["id"]
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

                news = pipeline_dtos[
                    (int(page_number) - 1)
                    * int(page_size) : (int(page_number))
                    * int(page_size)
                ]

        except Exception as e:
            print(e)
            news = []
            total = 0
        return { "sentiment": sentiment_statistic,  "result": news, "total_record": total}

    def translate(self, lang, content):
        lang_dict = {"en": "english", "ru": "russian", "cn": "chinese"}
        lang_code = lang_dict.get(lang)
        req = requests.post(
            settings.TRANSLATE_API,
            data=json.dumps({"language": lang_code, "text": content}),
        )
        if req.ok:
            return req.json().get("translate_text")
        else:
            return ""

    def get_history_statistic_by_id(self, pipeline_id, start_date, end_date, n_days):
        if start_date is not None and start_date != "":
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
        if end_date is not None and end_date != "":
            end_date = datetime.strptime(end_date, "%d/%m/%Y")
        return self.__job_service.get_history_statistic_by_id(
            pipeline_id, start_date, end_date, n_days
        )
