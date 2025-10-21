# GitHub Copilot – Python + FastAPI Best Practices 🚀

You are an expert in **Python** and **FastAPI** for modern web API development. Follow these guidelines:

---

## 🎯 Project Context  
– **FastAPI** for modern, high-performance web APIs with automatic documentation.  
– Use `.env` or config files for configuration management.  
– **Official Documentation**: https://fastapi.tiangolo.com/

---

## 📦 Python Package Management with UV

### **Why UV?**
- ⚡ 10-100x faster than pip
- 🚀 Single tool replacing pip, pip-tools, poetry, virtualenv, and more
- 🗂️ Universal lockfile (uv.lock) for reproducible builds
- 🐍 Manages Python versions automatically
- 💾 Global cache for disk-space efficiency
- 🛠️ Built-in project management with workspace support

### **Project Setup & Dependencies**
- Use `uv` for all dependency management and project configuration
- Project metadata stored in `pyproject.toml`
- Dependencies locked in `uv.lock` for reproducibility
- Virtual environments created automatically in `.venv`
- Never commit virtual environments or `uv.lock` manually

### **Environment Management**
```bash
# Initialize new project
uv init project-name

# Create virtual environment (automatic with uv sync/run)
uv venv

# Install Python version
uv python install 3.12

# Pin Python version for project
uv python pin 3.11

# Sync environment with lockfile
uv sync
```

### **Dependency Management**
```bash
# Add runtime dependency
uv add fastapi uvicorn requests

# Add dev dependency
uv add --dev pytest pytest-asyncio httpx black flake8

# Remove dependency
uv remove package_name

# Update all dependencies
uv lock --upgrade

# Install from lockfile
uv sync
```

### **Script Execution Patterns**
```bash
# Run script with uv (auto-manages environment)
uv run main.py

# Run with arguments
uv run main.py --date=20250724 --path=/downloads

# Run tests with pytest
uv run pytest

# Run specific test file
uv run pytest test/test_api.py

# Run FastAPI development server
uv run uvicorn app.main:app --reload
```

### **Project Structure Best Practices**
- Keep `pyproject.toml` in project root
- Commit `uv.lock` to version control
- Use `uv.lock` for reproducible builds across environments
- Store all test scripts in `./test` directory
- Store all documentation in `./doc` directory
- `.venv` automatically created and managed by uv

### **Common Commands for Development**
```bash
# Project initialization
uv init                      # Initialize new project
uv add package_name          # Add runtime dependency
uv add --dev package_name    # Add dev dependency
uv remove package_name       # Remove dependency
uv sync                      # Sync environment with lockfile
uv lock                      # Update lockfile

# Running code
uv run script.py             # Run Python script
uv run pytest               # Run tests
uvx tool_name               # Run tool without installing

# Python version management
uv python install 3.12      # Install Python version
uv python list              # List available Python versions
uv python pin 3.11          # Pin Python version for project
```

### **Development Workflow**
```bash
# Initial project setup
uv init my_fastapi_project
cd my_fastapi_project
uv python install 3.12
uv python pin 3.12

# Add dependencies
uv add "fastapi[standard]" uvicorn requests
uv add --dev pytest pytest-asyncio httpx black isort mypy

# Daily development commands
uv sync                      # Sync environment
uv run uvicorn app.main:app --reload  # Run FastAPI dev server
uv run pytest test/          # Run test suite

# Dependency management
uv add new_package           # Add new dependency
uv lock --upgrade            # Update all dependencies
uv sync                      # Apply changes
```

### **Migration from pip/requirements.txt**
```bash
# If you have requirements.txt, migrate to uv:
uv init --no-workspace

# Windows PowerShell
Get-Content requirements.txt | Where-Object { $_ -notmatch '^#' } | ForEach-Object { uv add $_ }

# Linux/Mac
cat requirements.txt | grep -v '^#' | xargs -n 1 uv add

# Or use pip interface temporarily
uv pip install -r requirements.txt
```

---

## ⚡ FastAPI Best Practices

### **API Development Philosophy**
- **Modern Python**: Use Python 3.8+ with full type hints support
- **Performance First**: Built on Starlette and Pydantic for maximum speed
- **Developer Experience**: Automatic interactive API docs with Swagger UI and ReDoc
- **Standards-Based**: Full OpenAPI and JSON Schema compliance

### **Project Structure & Organization**
```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app instance
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py       # API router
│   │       └── endpoints/   # Individual endpoint modules
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Settings management
│   │   └── security.py      # Authentication logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       ├── __init__.py
│       └── business_logic.py
├── tests/
├── requirements.txt
└── pyproject.toml
```

### **Core FastAPI Patterns**
```python
# main.py - Application factory pattern
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(
        title="My API",
        description="Production-ready API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app

app = create_app()
```

### **Pydantic Models & Validation**
```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)
    
    @validator('email')
    def email_must_be_lowercase(cls, v):
        return v.lower()

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # For SQLAlchemy compatibility
```

### **Dependency Injection & Security**
```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    # JWT token validation logic
    token = credentials.credentials
    # Validate and decode token
    return user

@app.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    return {"message": f"Hello {current_user.name}"}
```

### **Error Handling & HTTP Exceptions**
```python
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )

# Consistent error responses
def raise_not_found(item: str, item_id: int):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{item} with id {item_id} not found"
    )
```

### **API Routing & Versioning**
```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["users"])

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> UserResponse:
    # Business logic here
    pass

@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate) -> UserResponse:
    # Creation logic here
    pass

app.include_router(router)
```

### **Configuration & Environment Management**
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "My FastAPI App"
    admin_email: str
    database_url: str
    secret_key: str
    debug: bool = False
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

# Usage in endpoints
@app.get("/info")
async def app_info(settings: Settings = Depends(get_settings)):
    return {"app_name": settings.app_name}
```

### **Background Tasks & Async Operations**
```python
from fastapi import BackgroundTasks
import asyncio

async def send_notification(email: str, message: str):
    # Async notification logic
    await asyncio.sleep(1)  # Simulate async work
    print(f"Sent to {email}: {message}")

@app.post("/notify")
async def create_notification(
    email: str, 
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_notification, email, "Welcome!")
    return {"message": "Notification will be sent"}
```

### **Testing FastAPI Applications**
```python
from fastapi.testclient import TestClient
import pytest

@pytest.fixture
def client():
    return TestClient(app)

def test_create_user(client):
    response = client.post(
        "/api/v1/users",
        json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/users/1")
    assert response.status_code == 200
```

### **Performance & Production Best Practices**
- **Use async/await**: For I/O-bound operations (database, external APIs)
- **Connection Pooling**: Configure proper database connection pools
- **Response Models**: Always define response models for automatic documentation
- **Pagination**: Implement consistent pagination for list endpoints
- **Caching**: Use Redis or in-memory caching for frequently accessed data
- **Monitoring**: Integrate with APM tools (Sentry, DataDog, New Relic)
- **Rate Limiting**: Implement rate limiting for public APIs
- **Logging**: Use structured logging with correlation IDs

### **Development Tools Integration**
```bash
# Install FastAPI with all dependencies
uv add "fastapi[standard]" uvicorn

# Development server with auto-reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Install development tools
uv add --dev pytest pytest-asyncio httpx black isort mypy
```

---

## 🔍 Prompting Copilot  

Include in prompts:

1. **Your role**, e.g.  
   > "You are an expert Python + FastAPI engineer building production-ready APIs."

2. **What goal you're solving**, e.g.  
   > "Create a FastAPI endpoint with authentication, validation, and proper error handling."

3. **FastAPI Reminders**:  
   – Use **type hints** everywhere for automatic validation and documentation  
   – Implement **Pydantic models** for request/response schemas  
   – Use **dependency injection** for shared logic (auth, database connections)  
   – Follow **async/await** patterns for I/O operations  
   – Include **proper error handling** with HTTP status codes  
   – Add **response models** for automatic API documentation  

4. **Encourage maintainable code**:  
   – Use **fixtures** for setup/teardown  
   – Run tests in parallel where possible  
   – Implement **proper project structure** with clear separation of concerns

---

## ✅ Code Style & Quality  

- Follow PEP8 conventions (prefer `snake_case`, type hints).  
- Use **dataclasses** to structure scraped data.  
- Always call `browser.close()` or use context managers.  
- Add meaningful test names, e.g. `test_user_can_login_with_valid_account`.  
- Assert from the **user's perspective**, not implementation internals.

---

## 🛠️ Testing Practices  

### **API Testing (FastAPI)**
- Use **TestClient** for synchronous tests and **AsyncClient** for async tests
- **Mock external dependencies** (databases, third-party APIs) for unit tests
- Test **authentication flows** and **authorization** separately
- Validate **request/response schemas** using Pydantic models
- Test **error conditions** and proper HTTP status codes
- Use **pytest fixtures** for test data and app configuration
- Implement **database rollbacks** for integration tests

### **General Testing Guidelines**
- **Separate unit, integration, and E2E tests** into different directories
- Use **meaningful test names** that describe the behavior being tested
- **Test from the user's perspective**, not implementation internals
- **Automate test execution** in CI/CD pipelines
- **Monitor test performance** and optimize slow tests

---

Awesome—let’s layer **MVC (Model–View–Controller)** on top of your FastAPI + UV setup and bake in solid practices. FastAPI isn’t “classic MVC” (it’s API-first), but we can map it cleanly:

* **Model** → domain & persistence: Pydantic schemas (I/O) + SQLAlchemy ORM (DB).
* **View** → what the client sees: serialized responses (JSON) or Jinja2 templates if you render HTML.
* **Controller** → request orchestration: FastAPI routers/endpoints that call services and return views.

Below is a drop-in section you can append to your project instructions.

---

# 🧭 MVC Architecture for FastAPI (Clean, Testable & Scalable)

## MVC at a Glance (FastAPI mapping)

* **Models**

  * **Domain entities** (SQLAlchemy models, business rules).
  * **DTOs**/**Schemas** (Pydantic models for request/response).
* **Views**

  * **API responses** (Pydantic response models → JSON).
  * Optional **server-rendered HTML** (Jinja2 templates).
* **Controllers**

  * **Routers** (`APIRouter`) per resource/version that orchestrate:
    validation → service calls → return view (schema/HTML).

> Tip: Add a **Service** layer and **Repository** layer for cleaner separation:
>
> * **Service**: business logic (transactions, policies).
> * **Repository**: data access (SQLAlchemy queries).
>   Controllers never talk to the DB directly.

---

## 📁 Recommended Project Structure (MVC-friendly)

```
project/
├── app/
│   ├── main.py                         # App factory, middleware, router mounting
│   ├── core/
│   │   ├── config.py                   # Settings
│   │   ├── db.py                       # Engine/session, migrations hook
│   │   └── security.py                 # Auth/JWT, dependencies
│   ├── models/                         # "M" (domain + persistence)
│   │   ├── __init__.py
│   │   ├── entities/                   # SQLAlchemy ORM models (domain/persistence)
│   │   │   └── user.py
│   │   └── schemas/                    # Pydantic I/O schemas (views’ shapes)
│   │       └── user.py
│   ├── repositories/                   # Data access abstraction
│   │   └── user_repo.py
│   ├── services/                       # Business rules / transactions
│   │   └── user_service.py
│   ├── views/                          # "V" layer: response mapping/renderers
│   │   ├── __init__.py
│   │   └── renderers.py                # JSON or HTML helpers (optional Jinja2)
│   └── controllers/                    # "C" layer: API Routers
│       └── v1/
│           ├── __init__.py
│           └── users.py
├── tests/
│   ├── unit/        # services, repositories, utils
│   ├── api/         # controllers (TestClient/AsyncClient)
│   └── e2e/         # cross-layer flows (optional)
├── migrations/      # Alembic
├── pyproject.toml
└── uv.lock
```

**Naming conventions**

* SQLAlchemy entities: `PascalCase` (e.g., `User`).
* Pydantic schemas: `PascalCase` + suffix (`UserCreate`, `UserRead`).
* Routers/controllers: plural modules (`users.py`), route prefix `/users`.
* Services/Repos: singular resource + suffix (`user_service.py`, `user_repo.py`).

---

## 🔩 Wiring the Layers (concise example)

### Model: SQLAlchemy entity (domain/persistence)

```python
# app/models/entities/user.py
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, Integer, DateTime, func

class Base(DeclarativeBase): ...

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
```

### Model: Pydantic schemas (I/O contracts = “View shapes”)

```python
# app/models/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=100)

class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str
    created_at: datetime
```

### Repository: database access (no business logic)

```python
# app/repositories/user_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.user import User
from typing import Optional

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[User]:
        res = await self.session.execute(select(User).where(User.email == email))
        return res.scalar_one_or_none()

    async def create(self, *, email: str, name: str, hashed_password: str) -> User:
        user = User(email=email, name=name, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.flush()  # get PK
        return user
```

### Service: business rules, transactions, policies

```python
# app/services/user_service.py
from fastapi import HTTPException, status
from app.repositories.user_repo import UserRepository
from app.core.security import hash_password
from app.models.schemas.user import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession

class UserService:
    def __init__(self, repo: UserRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def register(self, data: UserCreate):
        if await self.repo.get_by_email(data.email):
            raise HTTPException(status_code=409, detail="Email already exists")

        user = await self.repo.create(
            email=data.email,
            name=data.name,
            hashed_password=hash_password(data.password),
        )
        await self.session.commit()
        await self.session.refresh(user)
        return user
```

### Controller: orchestrates request → service → response

```python
# app/controllers/v1/users.py
from fastapi import APIRouter, Depends, status
from app.models.schemas.user import UserCreate, UserRead
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService
from app.core.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/users", tags=["users"])

def get_user_service(session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session)
    return UserService(repo, session)

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, svc: UserService = Depends(get_user_service)):
    user = await svc.register(payload)
    return UserRead.model_validate(user, from_attributes=True)
```

### Views (HTML optional)

If you render HTML:

```python
# app/views/renderers.py
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")
# controller would return templates.TemplateResponse("page.html", {...})
```

If you only ship JSON, your **Pydantic response models are your “Views.”**

---

## 🧪 Testing the Layers (fast & isolated)

* **Repositories**: use an in-memory or containerized DB; assert SQL behavior (with rollbacks).
* **Services**: mock repositories; assert business rules (no DB required).
* **Controllers**: use `TestClient`/`AsyncClient`; assert HTTP status, schema shapes, headers.

```python
# tests/api/test_users.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user_ok(async_client: AsyncClient):
    resp = await async_client.post("/api/v1/users", json={
        "email": "a@b.com", "password": "Passw0rd!", "name": "Alice"
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "a@b.com"
```

> **Rule of thumb**
>
> * **Controllers**: zero business logic, zero DB logic.
> * **Services**: business logic only, no HTTP objects.
> * **Repositories**: persistence only, no business rules.

---

## 🧱 Cross-Cutting Best Practices (MVC + FastAPI)

* **Dependency Injection**: provide `get_session`, `get_current_user`, `get_service()` factories via `Depends`.
* **Transactions**: commit only in services; repositories do not commit.
* **Validation**: Pydantic for input; never trust controller payloads beyond schema.
* **Error Mapping**: Raise `HTTPException` in services for business conflicts (409, 422, 404).
* **Pagination**: controller parses `limit/offset` → service → repo uses `LIMIT/OFFSET`.
* **Idempotency**: for create endpoints if needed (e.g., via request id).
* **AuthN/Z**: security dependencies at controller level; authorization decisions in service.
* **Logging/Tracing**: add request IDs (middleware) and log at service boundaries.
* **DTO ≠ ORM**: never return ORM objects raw; always map to Pydantic response models.
* **Versioning**: mount routers under `/api/v1`, `/api/v2`.
* **OpenAPI**: set response models & error schemas for consistent docs.

---

## ⚙️ App Factory & Router Mounting

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.v1.users import router as users_router

def create_app() -> FastAPI:
    app = FastAPI(title="My API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"],
    )
    app.include_router(users_router)
    return app

app = create_app()
```

---

## 🗄️ Database & Migrations (async SQLAlchemy + Alembic)

```python
# app/core/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import Depends
from app.core.config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
```

* **Migrations**: configure **Alembic** to use the same models metadata; run via `uv run alembic upgrade head`.

---

## 🧰 Linting, Types, CI (keep controllers skinny)

* **black/isort/flake8/mypy** in dev deps.
* Enforce **no DB imports** in controllers via lint rules or simple code review.
* Unit tests for **services** carry most logic coverage; API tests validate integration.

---

## 🧱 Example Endpoint Checklist (Controller PR template)

* [ ] Request/response schemas defined (Pydantic).
* [ ] No business/DB logic in controller.
* [ ] Service method exists and covered by unit tests.
* [ ] Repository query covered by unit/integration tests.
* [ ] Errors mapped to proper HTTP status (404/409/422/401/403).
* [ ] Pagination, sorting, filtering (if list).
* [ ] Docs visible in `/docs` and consistent.

---

## 🔌 Using UV with MVC

* Keep the structure above; **UV** manages env & tooling as in your original guide.
* Add dev scripts to `pyproject.toml` for repeatable flows:

```toml
[tool.uv.scripts]
dev = "uvicorn app.main:app --reload"
test = "pytest -q"
migrate = "alembic upgrade head"
```

---
