from fastapi import APIRouter
from typing import *
from .models import Branch
from .services import *
import traceback
from fastapi import HTTPException

router = APIRouter()

@router.get("/get-branches")
def route_get_branches(search_text:str="", page_size:int=10, page_index:int=1)->Any:
    try: 
        data = get_branches(search_text, page_size, page_index)
        
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.get("/get-branch-by-id")
def route_get_branch_by_id(branch_id:str)->Branch:
    try: 
        data = get_branch(branch_id)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.get("/get-branch-dropdown")
def route_get_branch_dropdown()->Any:
    try: 
        data = get_branch_dropdown()
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))
    
@router.post("/insert-branch")
def route_insert_branch(branch: Branch)->str:
    try: 
        data = insert_branch(branch.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/update-branch")
def route_update_branch(branch: Branch)->int:
    try: 
        data = update_branch(branch.branch_id, branch.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/delete-branch")
def route_delete_branch(branch_ids:list[str])->int:
    try: 
        data = delete_branches(branch_ids)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))