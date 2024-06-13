from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Body, HTTPException, Path, status
from fastapi.responses import JSONResponse

from app.resource_monitor.models import Server, ResourceMonitor, ResourceMonitorCreate

from app.resource_monitor.services import (
    insert_resource_monitors,
    get_average_monitor as get_avg_monitor_service,
)
from app.resource_monitor import services
from datetime import datetime
import pytz

router = APIRouter()


@router.post("/schedule-update")
async def create_insert_resource_monitor(body: ResourceMonitorCreate):
    try:
        server_ip = body.server_ip
        server_name = body.server_name
        num_cpu = body.num_cpu
        total_ram = body.total_ram
        total_disk = body.total_disk
        is_active = body.is_active
        timestamp = body.timestamp
        cpu = body.cpu
        ram = body.ram
        disk = body.disk

        server = Server(
            server_ip=server_ip,
            server_name=server_name,
            num_cpu=num_cpu,
            total_ram=total_ram,
            total_disk=total_disk,
            is_active=is_active,
        )
        resource_monitor = ResourceMonitor(
            id=id,
            server_name=server_name,
            timestamp= datetime.isoformat(timestamp),
            cpu=cpu,
            ram=ram,
            disk=disk,
        )
        await insert_resource_monitors(server.dict(), resource_monitor.dict())
        return {"message": "update successfully!"}
    except Exception as err:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=None
        )


@router.get("/get-average-monitor")
async def get_average_monitor():
    try:
        data = await get_avg_monitor_service()
        print(data)
        return data
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=None
        )


@router.get("/get-server-details")
async def get_server_details():
    try:
        data = await services.get_server_details()
        return data
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=None
        )
