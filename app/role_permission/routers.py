from fastapi import APIRouter
from typing import *
from .models import InsertRolePermission
from .services import *
import traceback
from fastapi import HTTPException

router = APIRouter()

@router.get("/get-action-by-role-function-id")
def route_get_action_by_role_function_id(role_function_id:str="")->Any:
    try: 
        data = get_action_by_role_function_id(role_function_id)
        
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))
    
@router.post("/insert-role-permission")
async def route_insert_role_permission(role_permission: InsertRolePermission)->str:
    try: 
        data = await insert_role_permission(role_permission.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

