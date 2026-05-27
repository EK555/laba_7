from app.core.database_mongo import get_db
from bson import ObjectId
from datetime import datetime
from typing import Optional

class RefreshTokenRepository:
    
    @staticmethod
    async def save(user_id: str, token_hash: str, expires_at: datetime) -> dict:
        db = await get_db()
        token = {
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "revoked": False,
            "created_at": datetime.utcnow()
        }
        result = await db.refresh_tokens.insert_one(token)
        token["_id"] = str(result.inserted_id)
        return token
    
    @staticmethod
    async def find_valid_by_hash(token_hash: str) -> Optional[dict]:
        db = await get_db()
        token = await db.refresh_tokens.find_one({
            "token_hash": token_hash,
            "revoked": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        if token:
            token["_id"] = str(token["_id"])
            return token
        return None
    
    @staticmethod
    async def revoke(token_hash: str) -> None:
        db = await get_db()
        await db.refresh_tokens.update_one(
            {"token_hash": token_hash},
            {"$set": {"revoked": True}}
        )
    
    @staticmethod
    async def revoke_all_by_user(user_id: str) -> None:
        db = await get_db()
        await db.refresh_tokens.update_many(
            {"user_id": user_id, "revoked": False},
            {"$set": {"revoked": True}}
        )