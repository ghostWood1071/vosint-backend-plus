#from flask import jsonify, make_response, request

from .services import NlpService
from vosint_ingestion.nlp.hieu.vosintv3_text_clustering_main.code_doan.src.create_db_chude import create_db_chude
from vosint_ingestion.nlp.hieu.vosintv3_text_clustering_main.code_doan.src.create_db_linhvuc import create_db_linhvuc
from models import MongoRepository

class NlpController:

    def __init__(self):
        self.__nlp_service = NlpService()

    # def nlp_update_chude_text(self):
    #     return self.__nlp_service.nlp_update_chude_text()
        
    # def nlp_chude(self, id_chude, order, page_number, page_size):
    #     #user_id = request.args.get('user_id')
    #     #title = request.args.get('title')
    #     #order = request.args.get('order')
    #     #page_number = request.args.get('page_number')
    #     page_number = int(page_number) if page_number is not None else None
    #     #page_size = request.args.get('page_size')
    #     page_size = int(page_size) if page_size is not None else None

    #     # Create sort condition
    #     order_spec = order.split(',') if order else []

    #     # Calculate pagination information
    #     page_number = page_number if page_number else 1
    #     page_size = page_size if page_size else 20
    #     pagination_spec = {
    #         'skip': page_size * (page_number - 1),
    #         'limit': page_size
    #     }
    #     result = self.__nlp_service.nlp_chude(id_chude,order_spec=order_spec,
    #                                                        pagination_spec=pagination_spec)

    #     return {
    #             'success': True,
    #             "total_record":result[1],
    #             'result': result[0]
    #         }
    
    def update(self):
        return self.__nlp_service.update()
        
        
    def nlp_update_list_id(self,_id):
        return self.__nlp_service.nlp_update_list_id(_id)
    
    
    def nlp_update_list_all(self):
        return self.__nlp_service.nlp_update_list_all()
        


        