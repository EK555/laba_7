from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client.get_default_database()
        await self.client.admin.command('ping')
        print("MongoDB connected successfully")
        return self.db

    async def disconnect(self):
        if self.client:
            self.client.close()
            print("MongoDB disconnected")

mongo = MongoDB()

async def init_mongo():
    await mongo.connect()

async def get_db():
    return mongo.db