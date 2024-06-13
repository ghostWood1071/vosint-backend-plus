from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi.params import Body, Depends

from vosint_ingestion.nlp.hieu.vosintv3_text_clustering_main.code_doan.src.create_db_chude import create_db_chude
from vosint_ingestion.nlp.hieu.vosintv3_text_clustering_main.code_doan.src.create_db_linhvuc import create_db_linhvuc

from .nlpcontroller import NlpController

router = APIRouter()

nlp_controller = NlpController()

# @router.get('/api/nlp_chude/')
# def nlp_chude(id_chude, order=None, page_number=None, page_size=None,authorize: AuthJWT = Depends()):
#     # authorize.jwt_required()
#     # user_id = authorize.get_jwt_subject()
#     return JSONResponse(nlp_controller.nlp_chude(id_chude, order, page_number, page_size))

# @router.post('/api/nlp_update_chude_text/')
# def nlp_chude():
#     return JSONResponse(nlp_controller.nlp_update_chude_text())

@router.post('/api/update')
def nlp_update():
    return JSONResponse(nlp_controller.update())

@router.post('/api/update_list_id')
def nlp_update_list_id(_id):
    return JSONResponse(nlp_controller.nlp_update_list_id(_id))


@router.post('/api/nlp_update_list_all')
def nlp_update_list_all():
    return JSONResponse(nlp_controller.nlp_update_list_all())