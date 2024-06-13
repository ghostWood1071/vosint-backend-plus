from fastapi import APIRouter, Depends
from typing import *
from .models import Function
from .services import *
from .util import *
import traceback
from fastapi import HTTPException
from fastapi_jwt_auth import AuthJWT
from db.init_db import get_collection_client

router = APIRouter()

@router.get("/get-active-functions")
async def route_get_active_functions(authorize: AuthJWT = Depends(), plus: bool = False)->Any:
    try: 
        user_client = get_collection_client("users")
        authorize.jwt_required()
        user_id = authorize.get_jwt_subject()
        user = await user_client.find_one({"_id": ObjectId(user_id)})
        if(user.get("role_id") is None):
            return []

        data = await get_active_functions(user.get("role_id"), plus)
        data["data"] = get_function_tree(data["data"], 1, "0")
        return data 
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.get("/get-functions")
def route_get_functions(search_text:str="", page_size:int=10, page_index:int=1, plus: bool = False)->Any:
    try: 
        data = get_functions(search_text, page_size, page_index, plus)
        data["data"] = get_function_tree(data["data"], 1, "0")
        return data 
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.get("/get-function-by-id")
def route_get_function_by_id(function_id:str, plus: bool = False)->Function:
    try: 
        data = get_function(function_id, plus)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/insert-function")
def route_insert_function(function: Function, plus: bool = False)->str:
    try: 
        data = insert_function(function.dict(), plus)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/update-function")
def route_update_function(function: Function, plus: bool = False)->int:
    try: 
        data = update_function(function.function_id, function.dict(), plus)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/delete-function")
def route_delete_function(function_ids:list[str], plus: bool = False)->int:
    try: 
        data = delete_functions(function_ids, plus)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))