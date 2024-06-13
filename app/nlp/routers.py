from bson.objectid import ObjectId
from fastapi import APIRouter, status
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT

from app.user.services import find_user_by_id
from app.nlp.model import Summarize
import app.nlp.service as service

router = APIRouter()


@router.post("/summarize")
def summarize(model: Summarize):
    result = service.summarize(model.lang, model.title, model.paras, model.k)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
