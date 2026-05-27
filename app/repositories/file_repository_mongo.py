from app.core.database_mongo import get_db
from bson import ObjectId
from datetime import datetime
from typing import Optional, List

class FileRepository:
    
    @staticmethod
    async def create(file_data: dict) -> dict:
        db = await get_db()
        file_data["created_at"] = datetime.utcnow()
        file_data["updated_at"] = datetime.utcnow()
        result = await db.files.insert_one(file_data)
        file_data["_id"] = str(result.inserted_id)
        return file_data
    
    @staticmethod
    async def get_by_id(file_id: str) -> Optional[dict]:
        db = await get_db()
        try:
            file = await db.files.find_one({
                "_id": ObjectId(file_id),
                "deleted_at": None
            })
            if file:
                file["_id"] = str(file["_id"])
                return file
        except:
            pass
        return None
    
    @staticmethod
    async def soft_delete(file_id: str) -> bool:
        db = await get_db()
        result = await db.files.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"deleted_at": datetime.utcnow()}}
        )
        return result.modified_count > 0