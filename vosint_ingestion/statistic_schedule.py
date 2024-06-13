from datetime import timedelta
from bson.objectid import ObjectId
from datetime import datetime
from vosint_ingestion.models.mongorepository import MongoRepository

from vosint_ingestion.features.minh.Elasticsearch_main.elastic_main import (
    My_ElasticSearch,
)
import pytz
from vosint_ingestion.features.job.services.get_news_from_elastic import get_news_from_newsletter_id__


def status_source_news(day_space: int = 3, start_date=None, end_date=None):
    now = datetime.now()
    now = now.today() - timedelta(days=day_space)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=day_space + 1, seconds=-1)

    if start_date:
        start_of_day = datetime(
            int(start_date.split("/")[2]),
            int(start_date.split("/")[1]),
            int(start_date.split("/")[0]),
        )

    if end_date:
        end_date = datetime(
            int(end_date.split("/")[2]),
            int(end_date.split("/")[1]),
            int(end_date.split("/")[0]),
        )
        end_of_day = end_date.replace(hour=23, minute=59, second=59)

    start_of_day = start_of_day.strftime("%Y/%m/%d %H:%M:%S")
    end_of_day = end_of_day.strftime("%Y/%m/%d %H:%M:%S")

    list_hist, _ = MongoRepository().aggregate(
        "his_log",
        [
            {
                "$match": {
                    "created_at": {"$gte": start_of_day, "$lte": end_of_day},
                }
            }
        ],
    )

    list_pipelines, _ = MongoRepository().aggregate("pipelines", [])

    result = {
        "normal": 0,
        "error": 0,
        "unknown": 0,
    }

    if list_pipelines:
        for pipeline in list_pipelines:
            if pipeline["enabled"]:
                id = pipeline["_id"]

                is_completed = False
                is_unknown = True
                for his in list_hist:
                    if ObjectId(his["pipeline_id"]) == id:
                        is_unknown = False
                        if his["log"] == "completed":
                            is_completed = True
                            result["normal"] += 1
                            break

                if not is_completed and not is_unknown:
                    result["error"] += 1
                elif is_unknown:
                    result["unknown"] += 1

            else:
                result["unknown"] += 1
        result["last_update"] = datetime.now()
        in_db = MongoRepository().get_many("err_source_statistic", {})
        if in_db[1] == 0:
            MongoRepository().insert_one("err_source_statistic", result)
        else:
            MongoRepository().update_many(
                "err_source_statistic", {"_id": in_db[0][0]["_id"]}, {"$set": result}
            )
    return result



#def get_news_from_newsletter_id__(
def get_news_from_newsletter_id__2(
    list_id=None,
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
    # list_id = None
    query = None
    # index_name = "vosint"
    index_name = "vosint"
    my_es = My_ElasticSearch()

    # date-------------------------------------------
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

    # language----------------------------------------------------------
    if language_source:
        language_source_ = language_source.split(",")
        language_source = []
        for i in language_source_:
            language_source.append(i)

    # tin quan trọng -------------------------------------------------
    if vital == "1":
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

    # tin đánh dấu ---------------------------------------------------
    elif bookmarks == "1":
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

    # get newsletter --------------------------------------------------
    if news_letter_id != "" and news_letter_id != None:
        a = MongoRepository().get_one(
            collection_name="newsletter", filter_spec={"_id": news_letter_id}
        )

    # nếu là giỏ tin
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

    # nếu không là giỏ tin
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
                for i in a["keyword_cn"]["required_keyword"]:
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

    list_source_name = None
    if type == "source":
        name = MongoRepository().get_one(
            collection_name="info", filter_spec={"_id": id_nguon_nhom_nguon}
        )["name"]
        list_source_name = []
        list_source_name.append('"' + name + '"')
    elif type == "source_group":
        source_group = MongoRepository().get_one(
            collection_name="Source", filter_spec={"_id": id_nguon_nhom_nguon}
        )
        name = source_group.get("news")
        list_source_name = []
        for i in name:
            list_source_name.append('"' + i["name"] + '"')
    if text_search == None and list_source_name == None:
        pipeline_dtos = my_es.search_main(
            index_name=index_name,
            query=query,
            gte=start_date,
            lte=end_date,
            lang=language_source,
            sentiment=sac_thai,
            list_id=list_id,
            # size=page_size,
            size=(int(page_number)) * int(page_size),
            list_fields=list_fields,
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
            # size=page_size,
            size=(int(page_number)) * int(page_size),
            list_fields=list_fields,
        )
    else:
        if list_source_name == None:
            pipeline_dtos = my_es.search_main(
                index_name=index_name,
                query=text_search
                if (text_search != "" or text_search != None)
                else query,
                gte=start_date,
                lte=end_date,
                lang=language_source,
                sentiment=sac_thai,
                list_id=list_id,
                # size=page_size,
                size=(int(page_number)) * int(page_size),
                list_fields=list_fields,
            )
        else:
            pipeline_dtos = my_es.search_main(
                index_name=index_name,
                query=text_search
                if (text_search != "" or text_search != None)
                else query,
                gte=start_date,
                lte=end_date,
                lang=language_source,
                sentiment=sac_thai,
                list_id=list_id,
                list_source_name=list_source_name,
                # size=page_size,
                size=(int(page_number)) * int(page_size),
                list_fields=list_fields,
            )
        if list_id == None:
            list_id = []

        for i in range(len(pipeline_dtos)):
            list_id.append(pipeline_dtos[i]["_source"]["id"])

        pipeline_dtos = my_es.search_main(
            index_name=index_name,
            query=text_search,
            gte=start_date,
            lte=end_date,
            lang=language_source,
            sentiment=sac_thai,
            list_id=list_id,
            # list_source_name=list_source_name,
            # size=page_size,
            size=(int(page_number)) * int(page_size),
            list_fields=list_fields,
        )

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

    return pipeline_dtos


def top_news_by_topic():
    # Get total of news in seven days by topics (top 5) with key: data:class_linhvuc
    day_space = 7
    now = datetime.now()
    now = now.today() - timedelta(days=day_space - 1)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=day_space + 1, seconds=-1)

    start_of_day = start_of_day.strftime("%d/%m/%Y")
    end_of_day = end_of_day.strftime("%d/%m/%Y")

    data_fields, _ = MongoRepository().find(
        "newsletter", {"tag": "linh_vuc"}, {"_id": 1, "title": 1}
    )

    data = []

    for field in data_fields:
        data_es = None
        try:
            data_es = get_news_from_newsletter_id__(
                news_letter_id=field["_id"],
                page_size=10000,
                start_date=start_of_day,
                end_date=end_of_day,
            )
        except:
            pass

        if data_es:
            data.append({"_id": field["title"], "value": len(data_es)})

    if len(data) > 0:
        data = sorted(data, key=lambda x: x["value"], reverse=True)

    result = {}

    result["data"] = data[0:5]
    result["last_update"] = datetime.now()

    in_db = MongoRepository().get_many("top_statistic", {})
    if in_db[1] == 0:
        MongoRepository().insert_one("top_statistic", result)
    else:
        MongoRepository().update_many(
            "top_statistic", {"_id": in_db[0][0]["_id"]}, {"$set": result}
        )


def clear_slave_activity():
    try:
        past = datetime.now() - timedelta(hours=2)
        tz = pytz.timezone("Asia/Ho_Chi_Minh")
        time_pivot = past.astimezone(tz).strftime("%Y/%m/%d %H:%M:%S")
        MongoRepository().delete_many(
            "slave_activity", {"created_at": {"$lte": time_pivot}}
        )
    except Exception as e:
        print(e)

