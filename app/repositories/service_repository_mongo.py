from app.core.database_mongo import get_db
from bson import ObjectId
from datetime import datetime
from typing import List, Tuple, Optional

class ServiceRepository:
    
    @staticmethod
    async def create(data: dict) -> dict:
        db = await get_db()
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        result = await db.services.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return data
    
    @staticmethod
    async def get_by_id(service_id: str) -> Optional[dict]:
        db = await get_db()
        try:
            service = await db.services.find_one({
                "_id": ObjectId(service_id),
                "deleted_at": None
            })
            if service:
                service["_id"] = str(service["_id"])
                return service
        except:
            pass
        return None
    
    @staticmethod
    async def get_all(page: int, limit: int, user_id: str = None) -> Tuple[List[dict], int]:
        db = await get_db()
        skip = (page - 1) * limit
        query = {"deleted_at": None}
        
        if user_id:
            query["user_id"] = user_id
        
        total = await db.services.count_documents(query)
        cursor = db.services.find(query).skip(skip).limit(limit)
        services = []
        async for service in cursor:
            service["_id"] = str(service["_id"])
            services.append(service)
        
        return services, total
    
    @staticmethod
    async def update(service_id: str, data: dict) -> Optional[dict]:
        db = await get_db()
        data["updated_at"] = datetime.utcnow()
        result = await db.services.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": data}
        )
        if result.modified_count == 0:
            return None
        
        return await ServiceRepository.get_by_id(service_id)
    
    @staticmethod
    async def soft_delete(service_id: str) -> bool:
        db = await get_db()
        result = await db.services.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": {"deleted_at": datetime.utcnow()}}
        )
        return result.modified_count > 0