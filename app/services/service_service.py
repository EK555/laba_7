from app.repositories.service_repository_mongo import ServiceRepository
from app.core.cache import cache_service
from typing import List, Tuple

class ServiceService:

    @staticmethod
    async def create_service(service_data, user_id: str = None):
        """Создание услуги"""
        data = service_data.dict()
        if user_id:
            data["user_id"] = user_id
        
        service = await ServiceRepository.create(data)
        
        # Инвалидация кеша списков
        cache_service.delete_pattern("wp:services:list:*")
        
        return service

    @staticmethod
    async def get_service(service_id: str):
        """Получение услуги по ID"""
        cache_key = f"wp:services:item:{service_id}"
        cached = cache_service.get(cache_key)
        
        if cached:
            return cached
        
        service = await ServiceRepository.get_by_id(service_id)
        
        if service:
            # Преобразуем в словарь для кеша
            service_dict = service.dict()
            cache_service.set(cache_key, service_dict, ttl=300)
        
        return service

    @staticmethod
    async def get_services(page: int = 1, limit: int = 10, user_id: str = None) -> Tuple[List, int]:
        """Получение списка услуг с пагинацией и кешированием"""
        cache_key = f"wp:services:list:page:{page}:limit:{limit}"
        
        cached = cache_service.get(cache_key)
        if cached:
            return cached.get("services", []), cached.get("total", 0)
        
        services, total = await ServiceRepository.get_all(page, limit, user_id)
        
        # Преобразуем для сериализации
        services_data = []
        for s in services:
            services_data.append(s.dict())
        
        cache_service.set(cache_key, {"services": services_data, "total": total}, ttl=300)
        
        return services, total

    @staticmethod
    async def update_service(service_id: str, service_data):
        """Обновление услуги"""
        updated = await ServiceRepository.update(service_id, service_data.dict(exclude_unset=True))
        
        if updated:
            # Инвалидация кеша
            cache_service.delete(f"wp:services:item:{service_id}")
            cache_service.delete_pattern("wp:services:list:*")
            
            updated_dict = updated.dict()
            cache_service.set(f"wp:services:item:{service_id}", updated_dict, ttl=300)
        
        return updated

    @staticmethod
    async def delete_service(service_id: str):
        """Мягкое удаление услуги"""
        deleted = await ServiceRepository.soft_delete(service_id)
        
        if deleted:
            cache_service.delete(f"wp:services:item:{service_id}")
            cache_service.delete_pattern("wp:services:list:*")
        
        return deleted