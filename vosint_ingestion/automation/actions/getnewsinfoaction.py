import json
import time
from datetime import datetime

import requests
from common.internalerror import *
from elasticsearch import Elasticsearch
from features.minh.Elasticsearch_main.elastic_main import My_ElasticSearch
from models import HBaseRepository, MongoRepository
from models.mongorepository import MongoRepository
from utils import get_time_now_string_y_m_now

from ..common import ActionInfo, ActionType, ParamInfo, SelectorBy
from .baseaction import BaseAction

# from nlp.keyword_extraction.keywords_ext import Keywords_Ext
# from nlp.toan.v_osint_topic_sentiment_main.sentiment_analysis import topic_sentiment_classification
# from nlp.hieu.vosintv3_text_clustering_main_15_3.src.inference import text_clustering



my_es = My_ElasticSearch(host='http://192.168.1.99:9200', user='USER', password='PASS', verify_certs=False)

def call_tran(content = '', lang = 'en'):
    result = ''
    if lang == 'en':
        url = 'http://192.168.1.100:5002/predictions/en-vi-trans'
    elif lang == 'cn':
        url = 'http://192.168.1.100:5002/predictions/zh-vi-trans'
    elif lang == 'ru':
        url = 'http://192.168.1.100:5002/predictions/ru-vi-trans'
    headers = {'Content-Type': 'application/json'} # Set the content type of the request body

    # Make the POST request with the request body
    response = requests.post(url, headers=headers, data=content)
    try:
        result = response.text
    except:
        pass

    return result

class GetNewsInfoAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="get_news_info",
            display_name="Get News Infomation",
            action_type=ActionType.COMMON,
            readme="Lấy thông tin bài viết",
            param_infos=[
                ParamInfo(
                    name="by",
                    display_name="Select by",
                    # val_type="str",
                    val_type="select",
                    default_val=SelectorBy.CSS,
                    options=SelectorBy.to_list(),
                    validators=["required"],
                ),
                ParamInfo(
                    name="title_expr",
                    display_name="Title Expression",
                    val_type="str",
                    default_val="None",
                    validators=["required_"],
                ),
                ParamInfo(
                    name="author_expr",
                    display_name="Author Expression",
                    val_type="str",
                    default_val="None",
                    validators=["required_"],
                ),
                ParamInfo(
                    name="time",
                    display_name="Time Expression",
                    val_type="pubdate",
                    default_val={"time_expr":"None","time_format":["***",",","dd",",","mm",",","yyyy"]},
                    options = ["***","dd","mm","yyyy",",",".","/","_","-"," "],
                    validators=["required_"],
                ),
                ParamInfo(
                    name="content_expr",
                    display_name="Content Expression",
                    val_type="str",
                    default_val="None",
                    validators=["required_"],
                ),
        
            ],
            z_index=4,
        )

    def exec_func(self, input_val=None, **kwargs):
        collection_name = 'News'
        if not input_val:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["URL"], "msg": ["URL"]}
            )

        url = str(input_val)
        try:
            url = url.replace("<Page url='","").replace("'>","")
        except:
            pass
        # news_info = {}
        # page = input_val
        # by = self.params["by"]
        # time_expr = self.params["time"]['time_expr']
        # time_format = self.params["time"]['time_format']
        # print(time_format)
        # if time_expr != "None" and time_expr !="":
        #     elems = self.driver.select(page, by, time_expr)
        #     if len(elems) > 0:
        #         news_info["data:time"] = self.driver.get_content(elems[0])
        #         #print(news_info["data:time"])


        # a,b = MongoRepository().get_many(collection_name=collection_name,filter_spec={"data:url":url})
        # del a
        # if str(b) != '0':
        #     #print(b)
        #     print('url already exist')
        #     return {}
        
        
      
        by = self.params["by"]
        title_expr = self.params["title_expr"]
        author_expr = self.params["author_expr"]
        time_expr = self.params["time"]['time_expr']
        time_format = self.params["time"]['time_format']
        #print(type(time_format),time_format)
        #time_format = ['***',',','dd','/','mm','/','yyyy','-',"***"]
        content_expr = self.params["content_expr"]
        news_info = {}
        news_info['source_name'] = kwargs['source_name']
        news_info['source_host_name'] = kwargs['source_host_name']
        news_info['source_language'] = kwargs['source_language']
        news_info['source_publishing_country'] = kwargs['source_publishing_country']
        news_info['source_source_type'] = kwargs['source_source_type']
        news_info["data:class_chude"] = []
        news_info["data:class_linhvuc"] = []

        
        page = input_val
        check_content = False
        if title_expr != "None" and title_expr !="":
            elems = self.driver.select(page, by, title_expr)
            if len(elems) > 0:
                news_info["data:title"] = self.driver.get_content(elems[0])
                news_info["data:title_translate"]= ''
                #print('aaaaaaaaaaa',kwargs["source_language"])
                try:
                    if kwargs["source_language"] == "en":
                        news_info["data:title_translate"] = call_tran(content = news_info["data:title"].encode('utf-8'), lang='en').replace('vi: ','')
                    elif kwargs["source_language"] == "ru":
                        news_info["data:title_translate"] = call_tran(content = news_info["data:title"].encode('utf-8'), lang='ru').replace('vi: ','')
                    elif kwargs["source_language"] == "cn":
                        #print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
                        news_info["data:title_translate"] = call_tran(content = news_info["data:title"].encode('utf-8'), lang='cn').replace('vi: ','')
                except:
                    pass

        if author_expr != "None" and author_expr !="":
            elems = self.driver.select(page, by, author_expr)
            if len(elems) > 0:
                news_info["data:author"] = self.driver.get_content(elems[0])
        #if time_expr != "None" and time_expr !="":
        if True:
            try:
                #print('time_expr',time_expr)
                elems = self.driver.select(page, by, time_expr)
                if len(elems) > 0:
                    news_info["data:time"] = self.driver.get_content(elems[0])
                    time_string = news_info["data:time"]
                    #print(news_info["data:time"])
                    try:
                        format = [",",".","/","_","-"," "]
                        my_concat = lambda arr: ''.join(arr)
                        len_time_format = len(time_format)
                        time_result ={}
                        for i in range(len_time_format):
                            if time_format[i] in format:
                                if i > 0:
                                    name_time_format_1 = "time_" + str(time_format[i-1])
                                    #print(time_format[i])
                                    #print(time_string)
                                    index = time_string.index(time_format[i])# split the string at the delimiter
                                    #tg = time_string.split(time_format[i])
                                    tg = time_string
                                    time_string = time_string[index + 1:]
                                    if str(time_format[i-1]) == '***':
                                        continue
                                    
                                    time_result[f'{name_time_format_1}']=f'{tg[:index]}'.replace(' ','').replace('\n','').replace('\t','')          
                                elif i< (len_time_format - 1):
                                    tg = time_string.split(time_format[i])
                                    time_string = my_concat(tg[1:])
                                else:
                                    pass
                        news_info['pub_date']=''
                        try:
                            if time_result['time_yyyy'] != "None" and time_result['time_yyyy'] !="":
                                news_info['pub_date'] += time_result['time_yyyy']
                        finally:
                            news_info['pub_date'] += '-'
                        try:
                            if time_result['time_mm'] != "None" and time_result['time_mm'] !="":
                                news_info['pub_date'] += time_result['time_mm']
                        finally:
                            news_info['pub_date'] += '-'
                        try:
                            if time_result['time_dd'] != "None" and time_result['time_dd'] !="":
                                news_info['pub_date'] += time_result['time_dd']
                        except:
                            pass
                        finally:
                            try:
                                news_info['pub_date'] = datetime.strptime(str(news_info['pub_date']), "%Y-%m-%d")#.date()
                            except:
                                news_info['pub_date'] = get_time_now_string_y_m_now()
                    except:
                        news_info['pub_date'] = get_time_now_string_y_m_now()
            except:
                pass

        # else:
        #     news_info['pub_date'] = get_time_now_string_y_m_now()

        if content_expr != "None" and content_expr !="":
            elems = self.driver.select(page, by, content_expr)
            if len(elems) > 0:
                news_info["data:content"] = self.driver.get_content(elems[0])
                check_content = True

                news_info["data:content_translate"] = ''
                # try:
                #     if kwargs["source_language"] == "en":
                #         news_info["data:content_translate"] = call_tran_en_vi(news_info["data:content"]).replace('vi: ','')
                # except:
                #     pass
                
                try:
                    news_info['keywords'] = Keywords_Ext().extracting(document= news_info["data:content"],num_keywords =6)
                except:
                    news_info['keywords'] = []
                try:
                    class_text_clustering = text_clustering(sentence = str(news_info["data:content"]), class_name="class_chude")
                    news_info["data:class_chude"] = class_text_clustering
        
                except:
                    pass
                try:
                    class_text_clustering = text_clustering(sentence = str(news_info["data:content"]), class_name="class_linhvuc")
                    news_info["data:class_linhvuc"] = class_text_clustering
                except:
                    pass
                try:
                    kq = topic_sentiment_classification(news_info["data:content"])
                    if str(kq['sentiment_label']) == 'tieu_cuc':
                        kq = '2'
                    elif str(kq['sentiment_label']) == 'trung_tinh':
                        kq = '0'
                    elif str(kq['sentiment_label']) == 'tich_cuc':
                        kq = '1'
                    else:
                        kq = ''
                    news_info['data:class_sacthai'] = kq
                except:
                    pass

            news_info["data:url"] = url
        if content_expr != "None" and content_expr !="":
            elems = self.driver.select(page, by, content_expr)
            if len(elems) > 0:
                news_info["data:html"] = self.driver.get_html(elems[0])

                tmp_video = self.driver.select(from_elem=page,by='css',expr='figure')
                for i in tmp_video:
                    news_info["data:html"] = news_info["data:html"].replace(self.driver.get_html(i),'')


        check_url_exist = '0'
        a,b = MongoRepository().get_many(collection_name=collection_name,filter_spec={"data:url":url})
        del a
        if str(b) != '0':
        
            print('url already exist')
            check_url_exist = '1'

        if check_content and check_url_exist == '0':
            try:
                _id = MongoRepository().insert_one(collection_name=collection_name, doc=news_info)
                #print(type(_id))
            except:
                print("An error occurred while pushing data to the database!")

            #elastícearch
            try:
                #doc_es = {}
                doc_es = news_info.copy()
                # try:
                #     doc_es['_id'] = _id
                # except:
                #     pass
                try:
                    doc_es['id'] = str(doc_es['_id'])
                    doc_es.pop("_id", None)
                except:
                    pass
                try:
                    doc_es['data:title'] = news_info['data:title']
                except:
                    pass
                try:
                    doc_es['data:author'] = news_info['data:author']
                except:
                    pass
                try:
                    doc_es['data:time'] = news_info['data:time']
                except:
                    pass
                try:
                    doc_es['pub_date'] = str(news_info['pub_date']).split(' ')[0]+'T00:00:00Z'
                except:
                    pass
                try:
                    doc_es['data:content'] = news_info['data:content']
                except:
                    pass
                try:
                    doc_es['keywords'] = news_info['keywords']
                except:
                    pass
                try:
                    doc_es['data:url'] = news_info['data:url']
                except:
                    pass
                try:
                    doc_es['data:html'] = news_info['data:html']
                except:
                    pass
                try:
                    doc_es['data:class_chude'] = news_info['data:class_chude']
                except:
                    pass
                try:
                    doc_es['data:class_linhvuc'] = news_info['data:class_linhvuc']
                except:
                    pass
                try:
                    doc_es['source_name'] = news_info['source_name']
                except:
                    pass
                try:
                    doc_es['source_host_name'] = news_info['source_host_name']
                except:
                    pass
                try:
                    doc_es['source_language'] = news_info['source_language']
                except:
                    pass
                try:
                    doc_es['source_publishing_country'] = news_info['source_publishing_country']
                except:
                    pass
                try:
                    doc_es['source_source_type'] = news_info['source_source_type']
                except:
                    pass
                try:
                    doc_es['created_at'] = news_info['created_at'].split(' ')[0].replace('/','-')+'T'+news_info['created_at'].split(' ')[1]+'Z'
                except:
                    pass
                try:
                    doc_es['modified_at'] = news_info['modified_at'].split(' ')[0].replace('/','-')+'T'+news_info['modified_at'].split(' ')[1]+'Z'
                except:
                    pass
                try:
                    doc_es['data:class_sacthai'] = news_info['data:class_sacthai']
                except:
                    pass
                try:
                    doc_es['class_tinmau'] = news_info['class_tinmau']
                except:
                    pass
                try:
                    doc_es['class_object'] = news_info['class_object']
                except:
                    pass
                try:
                    doc_es['data:title_translate'] = news_info['data:title_translate']
                except:
                    pass
                try:
                    doc_es['data:content_translate'] = news_info['data:content_translate']
                except:
                    pass
                #print(doc_es)
                try:
                    print('aaaaaaaaaaaaaa',my_es.insert_document(index_name='vosint',id=doc_es['id'], document=doc_es))
                except:
                    print('insert elastic search false')
            except:
                print("An error occurred while pushing data to the database!")
            

        # if check_content and check_url_exist == '1':
        #     print('aaaaaaaaaaaaaaaaaaaaaa')
        #     try:
        #         a = MongoRepository().get_one(collection_name=collection_name,filter_spec={"data:url":url})
        #         #print('abcccccccccccccccccccccccccccccccccccccccccccc',a["_id"])
        #         news_info_tmp = news_info
        #         news_info_tmp["_id"] = str(a["_id"])
        #         MongoRepository().update_one(collection_name=collection_name, doc=news_info_tmp)
        #         print('update new ....')
        #     except:
        #         print("An error occurred while pushing data to the database!")

        return news_info
