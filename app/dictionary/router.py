from fastapi import APIRouter, File, UploadFile, Depends
from typing import *
from .model import *
from .service import *
import traceback
from fastapi import HTTPException
from fastapi_jwt_auth import AuthJWT
import os

router = APIRouter()

@router.post("/search")
def search_route(search_params:SearchParams):
    try:
        if search_params.search_text == "":
            search_params.search_text = None
        results = search_word(**search_params.dict())
        return results
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))

@router.post("/add")
def search_route(word:Word):
    try:
        inserted = add_word(word.dict())
        return inserted
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    
@router.post("/update")
def search_route(new_word:WordUpdate):
    try:
        results = update_word(new_word.dict())
        return results
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    
@router.post("/delete")
def search_route(ids:List[str] = []):
    try:
        deleted = delete_word(ids)
        return deleted
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))