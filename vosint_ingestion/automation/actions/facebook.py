from common.internalerror import *
from facebook.fb_canhan import fb_canhan
from facebook.fb_groups import fb_groups
from facebook.fb_page import fb_page

from ..common import ActionInfo, ActionType, ParamInfo, SelectorBy
from .baseaction import BaseAction
import json
import time
from models import MongoRepository

class FacebookAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="fb",
            display_name="Facebook",
            action_type=ActionType.COMMON,
            readme="fb",
            param_infos=[
                ParamInfo(
                    name="person",
                    display_name="Đối tượng theo dõi",
                    val_type="str",
                    default_val="",
                    validators=["required_"],
                ),
                ParamInfo(
                    name="type",
                    display_name="Đối tượng",
                    val_type="select",
                    default_val="",
                    options = ['Cá nhân','Groups','Page'],
                    validators=["required_"],
                )
            ],
            z_index=14,
        )

    def exec_func(self, input_val=None, **kwargs):
        collection_name = "facebook"
        # if not input_val:
        #     raise InternalError(
        #         ERROR_REQUIRED, params={"code": ["FROM_ELEM"], "msg": ["From element"]}
        #     )
        #self.driver.destroy()
        time.sleep(2)
        person = self.params["person"]
        person = str(person).split(',')
        for i in person:
            if str(self.params['type']) =='Cá nhân':
                datas = fb_canhan(browser=self.driver.get_driver(),link_person=i)
            elif str(self.params['type']) =='Groups':
                datas = fb_groups(browser=self.driver.get_driver(),link_person=i)
            else:
                datas = fb_page(browser=self.driver.get_driver(),link_person=i+"?v=timeline")
            #print(datas)
            for data in datas:
                check_url_exist = '0'
                a,b = MongoRepository().get_many(collection_name=collection_name,filter_spec={"id_data_ft":data['id_data_ft']})
                del a
                if str(b) != '0':
                
                    print('url already exist')
                    check_url_exist = '1'
                if check_url_exist == '0':
                    try:
                        print(data)
                        MongoRepository().insert_one(collection_name=collection_name, doc=data)
                    except:
                        print("An error occurred while pushing data to the database!")
                
                if check_url_exist == '1':
                    try:
                        a = MongoRepository().get_one(collection_name=collection_name,filter_spec={"id_data_ft":data['id_data_ft']})
                        #print('abcccccccccccccccccccccccccccccccccccccccccccc',a["_id"])
                        news_info_tmp = data
                        news_info_tmp["_id"] = str(a["_id"])
                        MongoRepository().update_one(collection_name=collection_name, doc=news_info_tmp)
                        print('update new ....')
                    except:
                        print("An error occurred while pushing data to the database!")
        # data_rs = {}
        # data_rs["data:content"] = data
        return data