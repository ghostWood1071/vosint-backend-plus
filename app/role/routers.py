from fastapi import APIRouter
from typing import *
from .models import Role
from .services import *
import traceback
from fastapi import HTTPException

router = APIRouter()

@router.get("/get-roles")
def route_get_roles(search_text:str="", page_size:int=10, page_index:int=1)->Any:
    try: 
        data = get_roles(search_text, page_size, page_index)
        
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.get("/get-role-by-id")
def route_get_role_by_id(role_id:str)->Role:
    try: 
        data = get_role(role_id)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.get("/get-role-dropdown")
def route_get_role_dropdown()->Any:
    try: 
        data = get_role_dropdown()
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))
    
@router.post("/insert-role")
def route_insert_role(role: Role)->str:
    try: 
        data = insert_role(role.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/update-role")
def route_update_role(role: Role)->int:
    try: 
        data = update_role(role.role_id, role.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/delete-role")
def route_delete_role(role_ids:list[str])->int:
    try: 
        data = delete_roles(role_ids)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))