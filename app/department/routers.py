from fastapi import APIRouter
from typing import *
from .models import Department
from .services import *
import traceback
from fastapi import HTTPException

router = APIRouter()

@router.get("/get-departments")
def route_get_departments(search_text:str="", page_size:int=10, page_index:int=1, branch_id:str="")->Any:
    try: 
        data = get_departments(search_text, page_size, page_index, branch_id)
        
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.get("/get-department-by-id")
def route_get_department_by_id(department_id:str)->Department:
    try: 
        data = get_department(department_id)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.get("/get-department-dropdown")
def route_get_department_dropdown()->Any:
    try: 
        data = get_department_dropdown()
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))
    
@router.post("/insert-department")
def route_insert_department(department: Department)->str:
    try: 
        data = insert_department(department.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/update-department")
def route_update_department(department: Department)->int:
    try: 
        data = update_department(department.department_id, department.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/delete-department")
def route_delete_department(department_ids:list[str])->int:
    try: 
        data = delete_departments(department_ids)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))