from fastapi import APIRouter
from typing import *
from .model import SearchParams, HistoryLog
from .service import *
import traceback
from fastapi import HTTPException

router = APIRouter()

@router.post("/add-action-log")
def route_add_action_log(log: HistoryLog):
    try:
        log_id = addLog(log.dict())
        return log_id
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/get-action-logs")
def route_get_action_logs(search_params: SearchParams):
    try:
        data = getLogs(search_params.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))