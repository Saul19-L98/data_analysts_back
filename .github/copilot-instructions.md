# GitHub Copilot – Python + Playwright Best Practices 🧪

You are an expert in **Python** and **Playwright** for end-to-end testing and scraping. Follow these guidelines:

---

## 🎯 Project Context  
– Playwright v1.x + Python.  
– Use `pytest-playwright` or plain scripts.  
– Tests must mimic real-user behavior: clicks, navigation, assertions.  
– Use `.env` or config files for test URLs and credentials.  
– **Follow official Playwright Python documentation**: https://playwright.dev/python/docs/intro

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
uv add playwright requests beautifulsoup4

# Add dev dependency
uv add --dev pytest black flake8

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
uv run pytest test/test_scraper.py

# Run tools without installation
uvx playwright install
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
uv init vidri_scraper
cd vidri_scraper
uv python install 3.12
uv python pin 3.12

# Add dependencies
uv add playwright requests beautifulsoup4
uv add --dev pytest black flake8

# Install Playwright browsers
uvx playwright install

# Daily development commands
uv sync                      # Sync environment
uv run main.py               # Execute scripts
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

## 🔍 Prompting Copilot  

Include in prompts:

1. Your role, e.g.  
   > "You are an expert Python + Playwright engineer writing robust E2E tests."

2. What goal you're solving, e.g.  
   > "Write a test that logs in, navigates to dashboard, and verifies greeting text."

3. Reminders:  
   – Use **web-first assertions**, **auto-waiting**, and **locators** (`page.locator()`) :contentReference[oaicite:1]{index=1}.  
   – Avoid arbitrary sleeps; prefer `locator.wait_for()` :contentReference[oaicite:2]{index=2}.  
   – Use stable selectors: test IDs, roles, labels :contentReference[oaicite:3]{index=3}.  
   – Isolate each test: new contexts, clean storage :contentReference[oaicite:4]{index=4}.

4. Encourage maintainable code:  
   – Use **Page Object Model** for shared UI structure :contentReference[oaicite:5]{index=5}.  
   – Use **fixtures** for setup/teardown :contentReference[oaicite:6]{index=6}.  
   – Run tests in parallel where possible :contentReference[oaicite:7]{index=7}.

---

## ✅ Code Style & Quality  

- Follow PEP8 conventions (prefer `snake_case`, type hints).  
- Use **dataclasses** to structure scraped data :contentReference[oaicite:8]{index=8}.  
- No hard-coded timeouts—fully rely on Playwright’s auto-wait features :contentReference[oaicite:9]{index=9}.  
- Always call `browser.close()` or use context managers.  
- Add meaningful test names, e.g. `test_user_can_login_with_valid_account`.  
- Assert from the **user’s perspective**, not implementation internals :contentReference[oaicite:10]{index=10}.

---

## 🛠️ Testing Practices  

- Define your E2E scope early (e.g., login, search, checkout) :contentReference[oaicite:11]{index=11}.  
- Avoid testing third-party integrations directly :contentReference[oaicite:12]{index=12}.  
- Use **mocked API responses** for speed and stability :contentReference[oaicite:13]{index=13}.  
- Include screenshots, traces, or videos for CI debugging :contentReference[oaicite:14]{index=14}.
- Run tests with `uv run pytest` to ensure proper environment isolation.
- Store all test files in the `./test` directory with clear naming conventions.

---
