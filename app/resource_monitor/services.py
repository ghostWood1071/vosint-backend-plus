import traceback
from typing import List, Optional

from bson import ObjectId
from fastapi import status
import pytz

from app.social.models import AddFollow, UpdateAccountMonitor
from db.init_db import get_collection_client
import pymongo
from datetime import datetime, timedelta

servers_client = get_collection_client("servers")
resource_monitors_client = get_collection_client("resource_monitors")


async def insert_resource_monitors(server, resource_monitor):
    # Xóa các bản ghi có cũ cách trước đó 1 giờ.
    current_time = datetime.utcnow()
    one_hour_ago = current_time - timedelta(hours=1)
    await resource_monitors_client.delete_many({"timestamp": {"$lt": one_hour_ago}})

    server_query = {"server_name": server["server_name"]}
    server_rp = await servers_client.find_one(server_query)

    if server_rp != None:
        update_operation = {
            "$set": {
                "num_cpu": server["num_cpu"],
                "total_ram": server["total_ram"],
                "total_disk": server["total_disk"],
            }
        }
        await servers_client.update_one(server_query, update_operation)

        # Kiểm tra xem đã có bản ghi nào được tạo chưa
        normal_heartbeat = 3
        count = await resource_monitors_client.count_documents(server_query)
        if count == 0:
            resource_monitors = []
            for i in range(normal_heartbeat):
                resource_monitors.append(resource_monitor.copy())
            await resource_monitors_client.insert_many(resource_monitors)
        else:
            await resource_monitors_client.insert_one(resource_monitor)
    else:
        await servers_client.insert_one(server)

        # Kiểm tra xem đã có bản ghi nào được tạo chưa
        normal_heartbeat = 3
        count = await resource_monitors_client.count_documents(server_query)
        if count == 0:
            for i in range(normal_heartbeat):
                await resource_monitors_client.insert_one(resource_monitor)
        else:
            await resource_monitors_client.insert_one(resource_monitor)





async def get_average_monitor():
    try:
        datetime_format = "%Y-%m-%d %H:%M:%S"
        all_servers = servers_client.find({})
        normal_heartbeat = 3
        sleeping_time = 600

        total_num_cpu = 0
        total_ram = 0
        total_disk = 0
        total_used_cpu = 0
        total_used_ram = 0
        total_used_disk = 0
        total_count = 0

        from_datetime = datetime.utcnow() - timedelta(seconds=sleeping_time * (normal_heartbeat + 1))
        current_time = datetime.utcnow()
        latest_resource_monitor = await resource_monitors_client.find_one(sort=[("timestamp", pymongo.DESCENDING)])

        if latest_resource_monitor is not None:
            lu_timestamp = datetime.strptime(latest_resource_monitor['timestamp']["$date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            # Trường hợp chưa có bản ghi nào
            lu_timestamp = datetime.utcnow()

        async for server in all_servers:
            # Kiểm tra server có đang active hay không
            heartbeat_query = {
                "timestamp": {"$gte": from_datetime, "$lte": current_time},
                "server_name": server["server_name"],
            }
            heartbeat = await resource_monitors_client.count_documents(heartbeat_query)

            if heartbeat < normal_heartbeat:
                continue
            last_resource_monitor = None
            total_count += 1
            total_num_cpu += float(server["num_cpu"])
            total_ram += float(server["total_ram"])
            total_disk += float(server["total_disk"])
            query = {
                "timestamp": {"$gte": from_datetime, "$lte": current_time},
                "server_name": server["server_name"],
            }
            sort = [("timestamp", -1)]

            last_resource_monitor = await resource_monitors_client.find_one(
                filter=query, sort=sort
            )
            if last_resource_monitor != None:
                total_used_cpu += float(last_resource_monitor["cpu"])
                total_used_ram += float(last_resource_monitor["ram"])
                total_used_disk += float(last_resource_monitor["disk"])
        if total_count == 0:
            return {
                "cpu_percent": 0,
                "ram_percent": 0,
                "disk_percent": 0,
                "timestamp": datetime.strftime(lu_timestamp + timedelta(hours=7), datetime_format),
            }
        cpu_percent = total_used_cpu / total_count
        ram_percent = (total_used_ram / total_ram) * 100
        disk_percent = (total_used_disk / total_disk) * 100
        data = {
            "cpu_percent": cpu_percent,
            "ram_percent": ram_percent,
            "disk_percent": disk_percent,
            "timestamp": datetime.strftime(lu_timestamp + timedelta(hours=7), datetime_format),
        }
        return data
    except Exception as e:
        print(e)
        traceback.print_exc()
        raise


async def get_server_details():
    try:
        datetime_format = "%Y-%m-%d %H:%M:%S"
        sleeping_time = 600
        normal_heartbeat = 3

        all_servers = servers_client.find({})
        total_count = 0
        from_datetime = datetime.utcnow() - timedelta(seconds=sleeping_time * normal_heartbeat)
        current_time = datetime.utcnow()
        server_details = []
        latest_resource_monitor = await resource_monitors_client.find_one(sort=[("_id", pymongo.DESCENDING)])

        if latest_resource_monitor is not None:
            lu_timestamp = datetime.strptime(latest_resource_monitor['timestamp']["$date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            # Trường hợp chưa có bản ghi nào
            lu_timestamp = datetime.utcnow()

        async for server in all_servers:

            # Kiểm tra server có đang active hay không
            heartbeat_query = {
                "timestamp": {"$gte": from_datetime, "$lte": current_time},
                "server_name": server["server_name"],
            }
            heartbeat = await resource_monitors_client.count_documents(heartbeat_query)

            if heartbeat < normal_heartbeat:
                server_detail = {
                    "server_ip": server["server_ip"],
                    "server_name": server["server_name"],
                    "cpu_percent": 0,
                    "ram_percent": 0,
                    "disk_percent": 0,
                    "is_active": False
                }
                server_details.append(server_detail)
                continue

            is_active = True

            total_count += 1

            query = {
                "timestamp": {"$gte": from_datetime, "$lte": current_time},
                "server_name": server["server_name"],
            }
            sort = [("timestamp", -1)]
            print(query)
            last_resource_monitor = await resource_monitors_client.find_one(
                filter=query,
                sort=sort,
            )
            server_detail = {
                "server_ip": server["server_ip"],
                "server_name": server["server_name"],
                "cpu_percent": 0,
                "ram_percent": 0,
                "disk_percent": 0,
                "is_active": False
            }
            if last_resource_monitor != None:
                cpu_percent = last_resource_monitor["cpu"]
                disk_percent = (
                    float(last_resource_monitor["disk"])
                    / float(server["total_disk"])
                    * 100
                )
                ram_percent = (
                    float(last_resource_monitor["ram"])
                    / float(server["total_ram"])
                    * 100
                )
                server_detail = {
                    "server_ip": server["server_ip"],
                    "server_name": server["server_name"],
                    "cpu_percent": cpu_percent,
                    "ram_percent": ram_percent,
                    "disk_percent": disk_percent,
                    "is_active": is_active
                }

            server_details.append(server_detail)

        data = {
            "timestamp": datetime.strftime(lu_timestamp + timedelta(hours=7), datetime_format),
            "count": total_count,
            "server_details": server_details,
        }
        return data

    except Exception as e:
        traceback.print_exc()
        raise
