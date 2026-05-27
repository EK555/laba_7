from app.core.database_mongo import get_db
from bson import ObjectId
from datetime import datetime
from typing import Optional

class UserRepository:
    
    @staticmethod
    async def find_by_email(email: str) -> Optional[dict]:
        db = await get_db()
        user = await db.users.find_one({
            "email": email,
            "deleted_at": None
        })
        if user:
            user["_id"] = str(user["_id"])
        return user
    
    @staticmethod
    async def find_by_id(user_id: str) -> Optional[dict]:
        print(f"[DEBUG] find_by_id called with: {user_id}")
        db = await get_db()
        try:
            from bson import ObjectId
            user = await db.users.find_one({
                "_id": ObjectId(user_id),
                "deleted_at": None
            })
            print(f"[DEBUG] find_by_id result: {user}")
            if user:
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            print(f"[DEBUG] find_by_id error: {e}")
            return None
    
    @staticmethod
    async def create(email: str, password_hash: str = None, yandex_id: str = None) -> dict:
        db = await get_db()
        user = {
            "email": email,
            "password_hash": password_hash,
            "yandex_id": yandex_id,
            "vk_id": None,
            "avatar_file_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "deleted_at": None
        }
        result = await db.users.insert_one(user)
        user["_id"] = str(result.inserted_id)
        return user
    
    @staticmethod
    async def update(user_id: str, data: dict) -> bool:
        db = await get_db()
        data["updated_at"] = datetime.utcnow()
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": data}
        )
        return result.modified_count > 0