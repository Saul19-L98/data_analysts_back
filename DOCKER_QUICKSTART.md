# 🐳 Quick Start - Docker

## TL;DR - Get Running in 60 Seconds

```bash
# 1. Clone and navigate
cd data_analyst_back

# 2. Create .env file with your AWS credentials
cat > .env << EOF
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
BEDROCK_AGENT_ID=your_agent_id
BEDROCK_AGENT_ALIAS_ID=your_alias_id
DEV_MODE=prod
EOF

# 3. Build and run
docker compose up -d

# 4. Test
curl http://localhost:8000/docs
```

---

## 📋 Common Commands

### Using Docker Compose (Recommended)

```bash
# Start production
docker compose up -d api

# Start development (hot reload)
docker compose --profile dev up api-dev

# View logs
docker compose logs -f api

# Stop
docker compose down

# Rebuild after changes
docker compose up -d --build
```

### Using Build Scripts

**Linux/Mac:**
```bash
# Make executable
chmod +x docker-build.sh

# Build
./docker-build.sh build

# Test
./docker-build.sh test

# Run
./docker-build.sh run
```

**Windows PowerShell:**
```powershell
# Build
.\docker-build.ps1 build

# Test
.\docker-build.ps1 test

# Run
.\docker-build.ps1 run
```

---

## 🎯 Development Workflow

```bash
# 1. Start dev container with hot reload
docker compose --profile dev up -d api-dev

# 2. Code changes auto-reload (no rebuild needed)
# Edit files in ./app/

# 3. View logs
docker compose logs -f api-dev

# 4. Test API
curl -X POST http://localhost:8001/api/v1/ingest \
  -F "file=@test_data/sample.csv" \
  -F "message=Analyze this data"

# 5. Stop when done
docker compose --profile dev down
```

---

## 🚀 Production Deployment

### AWS ECS/Fargate

1. **Push to ECR:**
   ```bash
   # Login
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin \
     123456789012.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and push
   ./docker-build.sh -r 123456789012.dkr.ecr.us-east-1.amazonaws.com -v 1.0.0 push
   ```

2. **Create ECS Task Definition** with:
   - Image: `<ecr_url>/data-analyst-back:1.0.0`
   - Port: 8000
   - Environment: Load from Parameter Store
   - Health check: `/docs`

### Docker Swarm

```bash
docker stack deploy -c docker-compose.yml data-analyst
```

### Standalone Server

```bash
# Pull image
docker pull your-registry/data-analyst-back:latest

# Run with restart policy
docker run -d \
  --name data-analyst-api \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  your-registry/data-analyst-back:latest
```

---

## 🔍 Troubleshooting

### Container won't start

```bash
# Check logs
docker compose logs api

# Common issues:
# 1. Missing .env file → Create it with AWS credentials
# 2. Port 8000 in use → Change port in docker-compose.yml
# 3. AWS credentials invalid → Verify in AWS Console
```

### Build fails

```bash
# Clean build (no cache)
docker compose build --no-cache

# Check Docker version
docker --version  # Need 20.10+

# Enable BuildKit
export DOCKER_BUILDKIT=1  # Linux/Mac
$env:DOCKER_BUILDKIT = "1"  # PowerShell
```

### Can't connect to AWS Bedrock

```bash
# Test AWS credentials
docker compose exec api aws sts get-caller-identity

# Check environment variables
docker compose exec api env | grep AWS
```

---

## 📚 Full Documentation

See [DOCKER.md](./DOCKER.md) for complete documentation including:
- Architecture details
- Performance optimizations
- Security best practices
- CI/CD integration
- Advanced configurations

---

## 🎓 Learning Resources

- [UV Docker Guide](https://docs.astral.sh/uv/guides/integration/docker/)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
