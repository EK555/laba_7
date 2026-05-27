from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database_mongo import mongo, init_mongo
from app.api.routes import auth
from app.api.v1.endpoints import services
from app.api.routes import files, profile

app = FastAPI(
    title="SPA Salon API",
    description="RESTful API для управления услугами SPA-салона с MongoDB",
    version="1.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/api/openapi.json" if settings.ENVIRONMENT != "production" else None,
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(services.router)
app.include_router(files.router)
app.include_router(profile.router)

# События запуска и остановки
@app.on_event("startup")
async def startup():
    await init_mongo()
    # Создаём бакет в MinIO, если его нет
    from app.services.storage_service import storage_service
    from app.core.config import settings
    storage_service.ensure_bucket_exists(settings.MINIO_BUCKET)
    print(f"Bucket '{settings.MINIO_BUCKET}' ensured")
    print("Application startup complete")

@app.on_event("shutdown")
async def shutdown():
    await mongo.disconnect()

@app.get("/")
async def root():
    return {"message": "SPA Salon API with MongoDB", "docs": "/api/docs"}

@app.get("/health")
async def health():
    return {"status": "healthy"}