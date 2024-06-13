from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime


class Server(BaseModel):
    server_ip: str = Field(...)
    server_name: str = Field(...)
    num_cpu: str = Field(...)
    total_ram: str = Field(...)
    total_disk: str = Field(...)
    is_active: bool = Field(...)


class ResourceMonitor(BaseModel):
    id: str = Field(default_factory=ObjectId, alias="_id")
    server_name: str = Field(...)
    timestamp: datetime = Field(...)
    cpu: str = Field(...)
    ram: str = Field(...)
    disk: str = Field(...)


class ResourceMonitorCreate(BaseModel):
    server_ip: str = Field(...)
    server_name: str = Field(...)
    num_cpu: str = Field(...)
    total_ram: str = Field(...)
    total_disk: str = Field(...)
    is_active: bool = Field(...)

    id: str = Field(default_factory=ObjectId, alias="_id")
    server_ip: str = Field(...)
    timestamp: datetime = Field(...)
    cpu: str = Field(...)
    ram: str = Field(...)
    disk: str = Field(...)
