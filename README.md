# Лабораторная работа №7: Объектное хранилище MinIO

## Описание проекта

RESTful API для управления услугами SPA-салона с системой аутентификации и авторизации на основе JWT токенов, кешированием через Redis и хранением файлов в объектном хранилище MinIO. В данной лабораторной работе реализовано объектное хранилище для файлов пользователей (аватары).

### Цель работы
- Изучить принципы работы с объектными хранилищами данных на примере MinIO.
- Освоить различия между хранением файлов в файловой системе, базе данных и объектном хранилище.
- Получить практические навыки подключения MinIO к веб-приложению.
- Реализовать загрузку и скачивание файлов с использованием потоков (Streams).
- Реализовать хранение метаданных файлов в MongoDB с связью с пользователем.
- Интегрировать функционал загрузки аватара пользователя в профиль.
- Обеспечить безопасность загружаемых файлов (валидация типов, размеров, доступ).

## Функциональность

### Лабораторная работа №2
- CRUD операции для услуг (создание, чтение, обновление, удаление)
- Пагинация списка услуг
- Мягкое удаление (soft delete)
- Валидация данных

### Лабораторная работа №3
- Регистрация и вход пользователей
- JWT аутентификация (Access Token + Refresh Token)
- Хеширование паролей с солью (bcrypt)
- HttpOnly cookies для безопасной передачи токенов
- Защита CRUD эндпоинтов через middleware
- Выход из системы (logout и logout-all)
- Обновление токенов через refresh token
- OAuth 2.0 вход через Яндекс (Yandex ID)

### Лабораторная работа №4
- Автоматическая документация API (Swagger UI / OpenAPI)
- Документация доступна только в режиме разработки (`/api/docs`)
- Интерактивное тестирование эндпоинтов через Swagger UI
- Примеры запросов и ответов для всех эндпоинтов

### Лабораторная работа №5
- Кеширование списка услуг в Redis (TTL 300 секунд)
- Инвалидация кеша при создании, обновлении и удалении услуг
- Хранение JTI (JWT ID) в Redis для мгновенного отзыва Access токенов
- Проверка JTI в middleware при каждом запросе

### Лабораторная работа №6
- **Замена PostgreSQL на MongoDB**
- Асинхронное подключение к MongoDB через Motor
- Документ-ориентированные модели данных (Beanie ODM)
- Сохранение всей бизнес-логики (CRUD, пагинация, soft delete)
- ID в формате ObjectId (строка)

### Лабораторная работа №7 
- **Интеграция MinIO (Object Storage)**
- Загрузка файлов с использованием потоков (Streams)
- Скачивание и удаление файлов
- Хранение метаданных файлов в MongoDB
- Установка аватара пользователя через profile
- Валидация файлов (MIME-типы: image/jpeg, image/png; размер до 10 MB)
- Доступ к файлам только для владельца
- Кеширование метаданных файлов в Redis (TTL 300 сек)

## Технологический стек

| Технология | Назначение |
|------------|-----------|
| Python 3.11 | Язык программирования |
| FastAPI | Веб-фреймворк |
| MongoDB 6 | Документоориентированная база данных (метаданные) |
| Motor | Асинхронный драйвер MongoDB |
| MinIO | Объектное хранилище (S3-совместимое) |
| Redis 7 | Кеширование и хранение сессий |
| JWT (PyJWT) | Токены доступа |
| bcrypt | Хеширование паролей |
| Docker / Docker Compose | Контейнеризация |

## Запуск через Docker

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/EK555/lab7.git
cd lab7
```
### 2. Создайте файл переменных окружения
```bash
cp .env.example .env
```
### 3. Запустите приложение
```bash
docker-compose up --build
```
## Локальный запуск (без Docker)

### 1. Запустить MongoDB и Redis в Docker
```bash
docker-compose up -d mongo redis minio
```
### 2. Создать виртуальное окружение
```bash
python -m venv .venv
.venv\Scripts\activate
```
### 3. Установить зависимости
```bash
pip install -r requirements.txt
```
### 4. Запустить сервер
```bash
uvicorn app.main:app --reload --port 8000
```
## Переменные окружения (.env.example)
```env
# MongoDB
MONGO_URI=mongodb://mongo:27017/spa_db

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minio_admin
MINIO_SECRET_KEY=minio_secure_password_change_in_prod
MINIO_BUCKET=spa-files
MINIO_USE_SSL=false
MAX_FILE_SIZE=10485760

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_secure_password_change_in_prod
CACHE_TTL_DEFAULT=300
CACHE_TTL_JWT=900

# JWT
JWT_ACCESS_SECRET=supersecretaccesstokenkey1234567890
JWT_REFRESH_SECRET=supersecretrefreshtokenkey0987654321
JWT_ACCESS_EXPIRES_MINUTES=15
JWT_REFRESH_EXPIRES_DAYS=7

# Yandex OAuth
YANDEX_CLIENT_ID=12d2dfd57e284f839df7db343baba588
YANDEX_CLIENT_SECRET=b80ddc5f728c493db850328fda757260
YANDEX_CALLBACK_URL=http://localhost:8000/auth/oauth/yandex/callback
O_AUTH_STATE_SECRET=random_string_for_state_encryption

# Приложение
PORT=8000
APP_NAME="SPA Salon API"
ENVIRONMENT=development
```
## База данных (MongoDB)

В проекте используется MongoDB. Метаданные файлов хранятся в коллекции files.

### Полезные команды MongoDB

```bash
# Подключиться к MongoDB
docker exec -it fastapi_spa_mongo mongosh

# Показать все базы данных
show dbs

# Переключиться на базу данных spa_db
use spa_db

# Показать все коллекции
show collections

# Посмотреть метаданные файлов
db.files.find().pretty()

# Посмотреть всех пользователей
db.users.find().pretty()

# Посмотреть услуги
db.services.find().pretty()

# Посмотреть Refresh токены
db.refresh_tokens.find().pretty()

# Посмотреть конкретного пользователя по email
db.users.find({ email: "test@example.com" }).pretty()

# Посмотреть конкретную услугу по ID
db.services.find({ _id: ObjectId("69fc908e68066fab16cae575") }).pretty()

# Выйти
exit
```

## API Эндпоинты

### Документация API

Проект использует автоматическую документацию OpenAPI (Swagger).

| Режим | Доступность | URL |
|-------|-------------|-----|
| Development | Доступна | `http://localhost:8000/api/docs` |
| Production | Недоступна (404) | — |

### Аутентификация

| Метод | URL | Описание | Доступ |
|-------|-----|----------|--------|
| POST | `/auth/register` | Регистрация пользователя | Public |
| POST | `/auth/login` | Вход (установка cookies) | Public |
| POST | `/auth/refresh` | Обновление токенов | Public |
| GET | `/auth/whoami` | Проверка статуса аутентификации | Private |
| POST | `/auth/logout` | Выход из текущей сессии | Private |
| POST | `/auth/logout-all` | Выход со всех устройств | Private |
| GET | `/auth/oauth/yandex` | Инициация входа через Яндекс | Public |
| GET | `/auth/oauth/yandex/callback` | Обработка callback от Яндекса | Public |

### Работа с файлами

| Метод | URL | Описание | Доступ |
|-------|-----|----------|--------|
| POST | `/files/upload` | Загрузка файла в MinIO | Private |
| GET | `/files/{file_id}` | Скачивание файла по ID | Private (только владелец) |
| DELETE | `/files/{file_id}` | Удаление файла (soft delete) | Private (только владелец) |

### Профиль пользователя

| Метод | URL | Описание | Доступ |
|-------|-----|----------|--------|
| GET | `/profile/` | Получение профиля текущего пользователя | Private |
| POST | `/profile/` | Обновление профиля (установка аватара) | Private |

### Услуги (CRUD)

| Метод | URL | Описание | Доступ |
|-------|-----|----------|--------|
| GET | `/api/v1/services?page=1&limit=10` | Получить список услуг (с пагинацией) | Private |
| GET | `/api/v1/services/{id}` | Получить услугу по ID | Private |
| POST | `/api/v1/services` | Создать новую услугу | Private |
| PUT | `/api/v1/services/{id}` | Полностью обновить услугу | Private |
| PATCH | `/api/v1/services/{id}` | Частично обновить услугу | Private |
| DELETE | `/api/v1/services/{id}` | Мягкое удаление услуги | Private |

**Важно:** Все эндпоинты, помеченные как `Private`, требуют валидный Access Token в cookies. Эндпоинты с пометкой "только владелец" дополнительно проверяют, что ресурс принадлежит текущему пользователю.

 ## Кеширование (Redis)

### Как работает кеширование:

| Ключ кеша | Данные | TTL | Инвалидация |
|-----------|--------|-----|-------------|
| `wp:services:list:page:{page}:limit:{limit}` | Список услуг с пагинацией | 300 сек | POST, PUT, PATCH, DELETE |
| `wp:auth:user:{id}:access:{jti}` | JTI Access токена | 900 сек | Logout, Logout-all |
| `wp:files:{file_id}:meta` | Метаданные файла | 300 сек | DELETE файла |

### Проверка кеша через Redis CLI

```bash
# Подключиться к Redis
docker exec -it fastapi_spa_redis redis-cli --pass redis_secure_password_change_in_prod

# Посмотреть все ключи
KEYS 'wp:*'

# Получить значение ключа списка услуг
GET wp:services:list:page:1:limit:10
```

### Примеры запросов

## Аутентификация
1. Регистрация пользователя
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"12345678"}'
```
Ожидаемый ответ:
```json
{
  "message": "Пользователь успешно зарегистрирован"
}
```
2. Вход (логин)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"12345678"}' \
  -c cookies.txt
```
Ожидаемый ответ:
```json
{
  "message": "Вход выполнен успешно",
  "user": {
    "id": "6a17649b3841a3074d94cb46",
    "email": "test@example.com"
  }
}
```

3. Загрузка файла (аватар)
```bash
curl -X POST http://localhost:8000/files/upload \
  -F "file=@avatar.jpg" \
  -b cookies.txt
```
Ожидаемый ответ:
```json
{
  "file_id": "6a176e070e047f45d8820f4f",
  "message": "Файл успешно загружен"
}
```

Запомните file_id — он понадобится для следующих шагов.

4. Получение профиля (до установки аватара)
```bash
curl -X GET http://localhost:8000/profile/ -b cookies.txt
```
Ожидаемый ответ:
```json
{
  "id": "6a17649b3841a3074d94cb46",
  "email": "test@example.com",
  "avatar_file_id": null,
  "has_avatar": false
}
```

5. Установка аватара
```bash
curl -X POST http://localhost:8000/profile/ \
  -H "Content-Type: application/json" \
  -d '{"avatar_file_id":"6a176e070e047f45d8820f4f"}' \
  -b cookies.txt
```
Ожидаемый ответ:
```json
{
  "id": "6a17649b3841a3074d94cb46",
  "email": "test@example.com",
  "avatar_file_id": "6a176e070e047f45d8820f4f",
  "has_avatar": true
}
```

6. Скачивание файла
```bash
curl -X GET http://localhost:8000/files/6a176e070e047f45d8820f4f \
  -b cookies.txt --output downloaded_avatar.jpg
```
Ожидаемый ответ:
```json
{
  200 OK (файл скачан)
}
```

7. Проверка безопасности (доступ к чужому файлу)
  1) Зарегистрируйте второго пользователя:
  ```bash
  curl -X POST http://localhost:8000/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test2@example.com","password":"12345678"}'
  ```
  2) Войдите как второй пользователь и загрузите файл:
  ```bash
  curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test2@example.com","password":"12345678"}' \
  -c cookies2.txt

  curl -X POST http://localhost:8000/files/upload \
    -F "file=@avatar2.jpg" \
    -b cookies2.txt
  ```

  Запомните file_id_2.

  3) Попробуйте скачать файл второго пользователя первым пользователем:
  ```bash
  curl -X GET http://localhost:8000/files/{file_id_2} -b cookies.txt
  ```
  Ожидаемый ответ:
  ```json
  {
    "detail": "Нет доступа к этому файлу"
  }
  ```

8. Удаление файла
```bash
curl -X DELETE http://localhost:8000/files/6a176e070e047f45d8820f4f -b cookies.txt
```
Ожидаемый ответ:
```json
{
  204 No Content
}
```

9. Проверка MinIO Console
Откройте браузер: http://localhost:9001

Логин: minio_admin

Пароль: minio_secure_password_change_in_prod

Проверьте бакет spa-files — файл должен быть удалён

### Потоковая обработка файлов (Streams)

В соответствии с требованиями лабораторной работы, файлы обрабатываются потоково, без полной загрузки в оперативную память:

```python
# Получение размера файла без чтения в память
file.file.seek(0, 2)
file_size = file.file.tell()
file.file.seek(0)

# Загрузка файла в MinIO потоково
result = self.client.put_object(
    bucket_name=bucket,
    object_name=object_key,
    data=file.file,  # ← поток, не буфер
    length=file_size,
    content_type=file.content_type
)

# Скачивание файла потоково
return StreamingResponse(
    file_stream,
    media_type=mimetype,
    headers={"Content-Disposition": f'attachment; filename="{original_name}"'}
)
```

### Безопасность

- Пароли хешируются с использованием bcrypt (уникальная соль для каждого пароля)
- Access и Refresh токены передаются через HttpOnly cookies
- JTI (JWT ID) хранятся в Redis для мгновенного отзыва токенов
- Redis защищён паролем
- Ключи кеша имеют префикс `wp:`
- MongoDB защищён паролем (в production)
- Валидация MIME-типов файлов: только `image/jpeg`, `image/png`, `image/jpg`
- Ограничение размера файла: `MAX_FILE_SIZE = 10 MB`
- Проверка доступа к файлам: `file_meta["user_id"] == current_user["id"]`
- Soft delete: поле `deleted_at` в MongoDB
- JWT авторизация через middleware `authenticate`

### Документация API
После запуска приложения документация доступна по адресам:
-	Swagger UI: http://localhost:8000/api/docs
-	ReDoc: http://localhost:8000/api/redoc

