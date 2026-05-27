from fastapi import APIRouter, Depends, HTTPException, Query
import math
from app.services.service_service import ServiceService
from app.schemas.service import ServiceResponse, ServiceCreate, ServiceUpdate
from app.schemas.pagination import PaginatedResponse
from app.middleware.auth import authenticate

router = APIRouter(prefix="/services", tags=["services"])

@router.get("/", response_model=PaginatedResponse[ServiceResponse])
async def get_services(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(authenticate)
):
    services, total = await ServiceService.get_services(page, limit, current_user['id'])
    total_pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedResponse(
        data=services,
        meta={
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    )

@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: str,
    current_user: dict = Depends(authenticate)
):
    service = await ServiceService.get_service(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.post("/", response_model=ServiceResponse, status_code=201)
async def create_service(
    service: ServiceCreate,
    current_user: dict = Depends(authenticate)
):
    result = await ServiceService.create_service(service, current_user['id'])
    return result

@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str,
    service: ServiceCreate,
    current_user: dict = Depends(authenticate)
):
    updated = await ServiceService.update_service(service_id, ServiceUpdate(**service.dict()))
    if not updated:
        raise HTTPException(status_code=404, detail="Service not found")
    return updated

@router.patch("/{service_id}", response_model=ServiceResponse)
async def patch_service(
    service_id: str,
    service: ServiceUpdate,
    current_user: dict = Depends(authenticate)
):
    updated = await ServiceService.update_service(service_id, service)
    if not updated:
        raise HTTPException(status_code=404, detail="Service not found")
    return updated

@router.delete("/{service_id}", status_code=204)
async def delete_service(
    service_id: str,
    current_user: dict = Depends(authenticate)
):
    deleted = await ServiceService.delete_service(service_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Service not found")
    return None