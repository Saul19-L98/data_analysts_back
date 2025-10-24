# Docker Container Startup Issues - Troubleshooting Guide

## Issue: Container Fails to Start with "No such file or directory"

### Problem Description

After building a multi-stage Docker image for FastAPI with UV package manager, the container would build successfully but fail to start with various errors related to Python executables not being found.

### Root Cause

When using UV's default behavior, it creates a virtual environment with symlinks pointing to UV-managed Python installations stored in `/root/.local/share/uv/python/`. In a multi-stage Docker build:

1. **Builder stage**: UV downloads and installs Python 3.13 to `/root/.local/share/uv/python/cpython-3.13.1-linux-x86_64-gnu/`
2. **Builder stage**: UV creates venv with symlinks pointing to this location
3. **Runtime stage**: Only the venv is copied (via `COPY --from=builder /app/.venv /app/.venv`)
4. **Runtime stage**: The UV-managed Python installation is NOT copied
5. **Result**: Symlinks in the venv point to non-existent paths → "No such file or directory"

### Symptom Investigation

```bash
# Files appeared to exist when listed
$ docker run --rm data-analyst-back:latest ls /app/.venv/bin/
python  python3  python3.13  uvicorn  ...

# But couldn't be accessed with wildcards
$ docker run --rm data-analyst-back:latest ls -la /app/.venv/bin/python*
ls: cannot access '/app/.venv/bin/python*': No such file or directory

# Symlink revealed the issue
$ docker run --rm data-analyst-back:latest readlink -f /app/.venv/bin/python
/root/.local/share/uv/python/cpython-3.13.1-linux-x86_64-gnu/bin/python3.13
# ↑ This path doesn't exist in the runtime stage!
```

### Solution 1: Use `--python-preference only-system` (IMPLEMENTED)

Force UV to use the system Python instead of managing its own Python installation.

**Dockerfile changes:**

```dockerfile
# Stage 1: Builder
FROM python:3.13-slim-bookworm AS builder

# Install dependencies with system Python
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --python-preference only-system

# Install project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --python-preference only-system

# Stage 2: Runtime
FROM python:3.13-slim-bookworm  # ← MUST match builder stage version

# Copy venv - now contains symlinks to /usr/local/bin/python3.13 (exists!)
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
```

**Key points:**
- Both stages must use the **same Python version** (3.13 in this case)
- Symlinks now point to `/usr/local/bin/python3.13` which exists in both stages
- No need to copy UV-managed Python installations

### Solution 2: Copy UV-Managed Python (Alternative, NOT used)

Copy the UV-managed Python installation to the runtime stage:

```dockerfile
# In runtime stage, before copying venv
COPY --from=builder /root/.local/share/uv/python/ /root/.local/share/uv/python/
```

**Pros:**
- Allows using specific Python versions not available in base images
- More isolation from system Python

**Cons:**
- Increases image size significantly
- Requires copying additional hidden directories
- More complex to maintain

### Solution 3: Use Editable Install (Alternative, NOT used)

Remove `--no-editable` flag to create simpler venv structure:

```dockerfile
RUN uv sync --frozen --no-dev --python-preference only-system
# Note: no --no-editable flag
```

**Pros:**
- Simpler venv structure
- Easier to debug

**Cons:**
- Requires source code in runtime stage
- Slightly slower startup
- Not recommended for production

### Verification Steps

After implementing the fix:

1. **Verify symlink points to system Python:**
   ```bash
   docker run --rm data-analyst-back:latest readlink -f /app/.venv/bin/python
   # Should output: /usr/local/bin/python3.13
   ```

2. **Test container startup:**
   ```bash
   docker run -d --name test-api -p 8000:8000 --env-file .env data-analyst-back:latest
   docker logs test-api
   # Should show: INFO: Uvicorn running on http://0.0.0.0:8000
   ```

3. **Access API documentation:**
   ```bash
   curl http://localhost:8000/docs
   # Should return Swagger UI HTML
   ```

### Lessons Learned

1. **Multi-stage builds with UV**: Always use `--python-preference only-system` to avoid symlink issues
2. **Python version consistency**: Builder and runtime stages must use the same Python version
3. **Symlink debugging**: Use `readlink -f` to trace symlink targets in containers
4. **UV behavior**: By default, UV manages its own Python installations for reproducibility
5. **Docker layers**: Symlinks created in one stage may break when copying to another stage

### Related UV Documentation

- [UV Docker Integration](https://docs.astral.sh/uv/guides/integration/docker/)
- [UV Python Version Management](https://docs.astral.sh/uv/concepts/python-versions/)
- UV `--python-preference` flag: Controls how UV selects Python interpreters

### Prevention Checklist

- [ ] Both Docker stages use the same Python version
- [ ] Added `--python-preference only-system` to all `uv sync` commands
- [ ] Tested symlinks point to existing paths: `readlink -f /app/.venv/bin/python`
- [ ] Container starts successfully and logs show Uvicorn running
- [ ] API endpoints are accessible (test /docs)

---

**Status**: ✅ **RESOLVED**  
**Fix Applied**: 2025-01-24  
**Docker Image**: `data-analyst-back:latest`  
**Container**: Running successfully on port 8000
