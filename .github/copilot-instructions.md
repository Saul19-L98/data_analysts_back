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
