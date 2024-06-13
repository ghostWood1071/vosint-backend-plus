import datetime
import json

from automation import Session
from common.internalerror import *
from features.pipeline.services import PipelineService
from logger import Logger
from models import HBaseRepository, MongoRepository
from scheduler import Scheduler
from utils import get_time_now_string
import requests
from core.config import settings

# from models import MongoRepository
from features.minh.Elasticsearch_main.elastic_main import My_ElasticSearch

# from nlp.hieu.vosint_v3_document_clustering_main_16_3.create_keyword import Create_vocab_corpus
# from nlp.keyword_extraction.keywords_ext import Keywords_Ext


# def start_job(actions: list[dict], pipeline_id=None):
#     session = Session(
#         driver_name="playwright",
#         storage_name="hbase",
#         actions=actions,
#         pipeline_id=pipeline_id,
#     )
#     # print('aaaaaaaaaaaa',pipeline_id)
#     return session.start()


def start_job(pipeline_id=None):
    request = requests.post(f"{settings.PIPELINE_API}/Job/api/start_job/{pipeline_id}")
    if not request.ok:
        raise Exception(request.json())
    # print("hello i'm the best programmer in the world")


class JobService:
    def __init__(self):
        self.__pipeline_service = PipelineService()
        self.__mongo_repo = MongoRepository()
        self.__elastic_search = My_ElasticSearch()

    # control job crawl
    # ----------------------------------------------------------------------------------------------------
    # start job imidiately
    def run_only(self, job_id: str, mode_test=None):
        request = requests.post(
            f"{settings.PIPELINE_API}/Job/api/run_only_job/{job_id}",
            params={"mode_test": mode_test},
        )
        if not request.ok:
            raise Exception(request.json())
        return request.json()

    def run_one_foreach(self, pipeline_id: str):
        return self.run_only(pipeline_id, None)

    def test_only(self, id: str):
        pipeline_dto = self.__pipeline_service.get_pipeline_by_id(id)
        return pipeline_dto.schema

    # add single job to scheduler
    def start_job(self, pipeline_id: str):
        pipeline_dto = self.__pipeline_service.get_pipeline_by_id(pipeline_id)
        if not pipeline_dto:
            raise InternalError(
                ERROR_NOT_FOUND,
                params={
                    "code": ["PIPELINE"],
                    "msg": [f"pipeline with id: {pipeline_id}"],
                },
            )

        if not pipeline_dto.enabled:
            raise InternalError(
                ERROR_NOT_FOUND,
                params={
                    "code": ["PIPELINE"],
                    "msg": [f"Pipeline with id: {pipeline_id}"],
                },
            )
        Scheduler.instance().add_job(
            pipeline_id, start_job, pipeline_dto.cron_expr, args=[pipeline_id]
        )

    # add multiple job to
    def start_all_jobs(self, pipeline_ids: list[str] = None):
        # Split pipeline_ids from string to list of strings
        pipeline_ids = pipeline_ids.split(",") if pipeline_ids else None

        enabled_pipeline_dtos = self.__pipeline_service.get_pipelines_off(pipeline_ids)

        for pipeline_dto in enabled_pipeline_dtos:
            try:
                Scheduler.instance().add_job(
                    pipeline_dto["_id"],
                    start_job,
                    pipeline_dto["cron"],
                    args=[pipeline_dto["_id"]],
                )
            except InternalError as error:
                Logger.instance().error(str(error))

    def stop_job(self, id: str):
        Scheduler.instance().remove_job(id)

    def stop_all_jobs(self, pipeline_ids: list[str] = None):
        # Split pipeline_ids from string to list of strings
        pipeline_ids = pipeline_ids.split(",") if pipeline_ids else None

        enabled_pipeline_dtos = self.__pipeline_service.get_pipelines_on(pipeline_ids)

        for pipeline_dto in enabled_pipeline_dtos:
            try:
                Scheduler.instance().remove_job(pipeline_dto.get("_id"))
            except InternalError as error:
                Logger.instance().error(str(error))

    # -------------------------------------------------------------------------------------------
    def translate(self, language: str, content: str):
        result = ""
        try:
            lang_dict = {"cn": "chinese", "ru": "russia", "en": "english"}
            lang_code = lang_dict.get(language)
            req = requests.post(
                settings.TRANSLATE_API,
                data=json.dumps({"language": lang_code, "text": content}),
            )
            result = req.json().get("translate_text")
            if not req.ok:
                raise Exception()
        except:
            result = ""
        return result

    def create_required_keyword(self, newsletter_id):
        a = self.__mongo_repo.get_one(
            collection_name="newsletter", filter_spec={"_id": newsletter_id}
        )["news_samples"]
        # print('len aaaaaaaaaa',len(a))
        list_keyword = []
        for i in a:
            content = i["title"] + i["content"]
            lang = i.get("lang") if i.get("lang") else "vi"
            tmp_lang = "vi" if lang == "cn" or lang == "ru" else lang
            if lang == "cn" or lang == "ru":
                content = self.translate(lang, content)
            body = json.dumps({"text": content, "number_keyword": 10, "lang": tmp_lang})
            print(body)
            req = requests.post(settings.KEYWORD_EXTRACTION_API, body)

            if req.ok:
                b = req.json().get("translate_text")
            else:
                raise Exception("create keyword failed")
            list_keyword.append(",".join(b))
        doc = self.__mongo_repo.get_one(
            collection_name="newsletter", filter_spec={"_id": newsletter_id}
        )
        doc["required_keyword_extract"] = list_keyword
        self.__mongo_repo.update_one(collection_name="newsletter", doc=doc)

    def get_news_from_id_source(
        sefl,
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
        size = page_number * page_size
        if type == "source":
            name = sefl.__mongo_repo.get_one(
                collection_name="infor", filter_spec={"_id": id}
            )["name"]
            list_source_name = []
            list_source_name.append(name)
            if list_source_name == []:
                return []
            # print(name)
            # query = {
            #     'query': {
            #         'match': {
            #             'source_name': name
            #         }
            #     },
            #     'size':size
            # }
            # a = sefl.__elastic_search.query(index_name='vosint',query=query)
            a = sefl.__elastic_search.search_main(
                index_name="vosint",
                query=text_search,
                gte=start_date,
                lte=end_date,
                lang=language_source,
                sentiment=sac_thai,
                list_source_name=list_source_name,
            )
            for i in range(len(a)):
                a[i]["_source"]["_id"] = a[i]["_source"]["id"]
                a[i] = a[i]["_source"]
            return a

        elif type == "source_group":
            name = sefl.__mongo_repo.get_one(
                collection_name="Source", filter_spec={"_id": id}
            )["news"]
            # value = []
            list_source_name = []
            for i in name:
                list_source_name.append(i["name"])

            if list_source_name == []:
                return []
            # print(value)
            # query = {
            #     'query': {
            #         'terms': {
            #             'source_name': value
            #         }
            #     },
            #     'size':size
            # }
            # a = sefl.__elastic_search.query(index_name='vosint',query=query)
            a = sefl.__elastic_search.search_main(
                index_name="vosint",
                query=text_search,
                gte=start_date,
                lte=end_date,
                lang=language_source,
                sentiment=sac_thai,
                list_source_name=list_source_name,
            )
            for i in range(len(a)):
                a[i]["_source"]["_id"] = a[i]["_source"]["id"]
                a[i] = a[i]["_source"]
            return a

    def elt_search(
        self, start_date, end_date, sac_thai, language_source, text_search, ids
    ):
        my_es = My_ElasticSearch()
        pipeline_dtos = my_es.search_main(
            index_name="vosint",
            query=text_search,
            gte=start_date,
            lte=end_date,
            lang=language_source,
            sentiment=sac_thai,
            ids=ids,
        )
        return pipeline_dtos

    def get_result_job(self, News, order_spec, pagination_spec, filter):
        print(filter)
        results = self.__mongo_repo.get_many_News(
            News,
            order_spec=order_spec,
            pagination_spec=pagination_spec,
            filter_spec=filter,
        )
        # results['_id'] = str(results['_id'])
        # results['pub_date'] = str(results['pub_date'])
        return results  # pipeline_dto.schema #

    def get_log_history(self, id: str, order_spec, pagination_spec):
        results = self.__mongo_repo.get_many_his_log(
            "his_log",
            {"pipeline_id": id},
            order_spec=order_spec,
            pagination_spec=pagination_spec,
        )

        return results

    def get_log_history_last(self, id: str):
        results = self.__mongo_repo.get_many_his_log(
            "his_log", {"pipeline_id": id, "log": "error"}
        )
        return results

    def get_log_history_error_or_getnews(
        self, id: str, order_spec, pagination_spec, start_date=None, end_date=None
    ):
        date_arr = self.get_date_array(7, start_date, end_date)
        start_date_str = date_arr[0]
        end_date_str = date_arr[len(date_arr) - 1]
        query = {
            "$and": [
                {"pipeline_id": id},
                {
                    "$or": [
                        {
                            "actione": {
                                "$in": [
                                    "GetNewsInfoAction",
                                    "FeedAction",
                                    "FacebookAction",
                                    "TtxvnAction",
                                    "TwitterAction",
                                    "TiktokAction",
                                ]
                            }
                        },
                        {"log": "error"},
                        {"log": "inqueue"},
                    ]
                },
                {"created_at": {"$gte": f"{start_date_str} 00:00:00"}},
                {"created_at": {"$lte": f"{end_date_str} 23:59:59"}},
            ]
        }
        results = self.__mongo_repo.get_many_his_log(
            "his_log",
            query,
            order_spec=order_spec,
            pagination_spec=pagination_spec,
        )
        return results

    def get_completed_count_in_day_query(self, date_str):
        return {
            # date_str: {
            "$sum": {
                "$cond": [
                    {"$regexMatch": {"input": "$created_at", "regex": date_str}},
                    1,
                    0,
                ]
            }
            # }
        }

    def get_date_array(self, n=7, start_date=None, end_date=None):
        if start_date is None and end_date is not None:
            start_date = end_date - datetime.timedelta(days=n)
        if end_date is None and start_date is not None:
            end_date = start_date + datetime.timedelta(days=n)
        if start_date is None and end_date is None:
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=n)
        if start_date is not None and end_date is not None:
            range_days = end_date - start_date
            if range_days.days is not None and range_days.days != n:
                n = range_days.days + 1

        results = []
        for day_nth in range(n):
            results.append(
                datetime.datetime.strftime(
                    start_date + datetime.timedelta(days=day_nth), "%Y/%m/%d"
                )
            )
        return results

    def get_history_statistic_by_id(self, pipeline_id, start_date, end_date, n_days):
        date_arr = self.get_date_array(n_days, start_date, end_date)
        pipeline = [
            {"$match": {"pipeline_id": pipeline_id, "log": {"$regex": "completed"}}},
            {
                "$group": {
                    "_id": "$pipeline_id",
                }
            },
        ]
        for date in date_arr:
            pipeline[1].get("$group")[date] = self.get_completed_count_in_day_query(
                date
            )
        data = self.__mongo_repo.aggregate("his_log", pipeline)
        return data
