from fastapi import APIRouter
from typing import *
from .models import InsertRoleFunction
from .services import *
import traceback
from fastapi import HTTPException

router = APIRouter()

@router.get("/get-function-by-role-id")
def route_get_function_by_role_id(role_id:str="")->Any:
    try: 
        data = get_function_by_role_id(role_id)
        
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))
    
@router.post("/insert-role-function")
async def route_insert_role_function(role_function: InsertRoleFunction)->str:
    try: 
        data = await insert_role_function(role_function.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

