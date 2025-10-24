# =============================================================================
# Docker Build & Deploy Script for Data Analyst Backend (PowerShell)
# =============================================================================

param(
    [Parameter(Position=0)]
    [ValidateSet('build', 'test', 'push', 'run', 'clean', 'help')]
    [string]$Command = 'help',
    
    [string]$Version = 'latest',
    [string]$Registry = '',
    [switch]$Help
)

# Configuration
$ImageName = "data-analyst-back"
$ErrorActionPreference = "Stop"

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is not installed"
        exit 1
    }
    
    if (-not (docker buildx version 2>$null)) {
        Write-Warn "Docker BuildKit not available, using standard build"
    }
    
    Write-Info "Prerequisites check passed"
}

function Build-Image {
    Write-Info "Building Docker image: ${ImageName}:${Version}"
    
    $env:DOCKER_BUILDKIT = "1"
    
    docker build `
        --tag "${ImageName}:${Version}" `
        --tag "${ImageName}:latest" `
        --build-arg BUILDKIT_INLINE_CACHE=1 `
        .
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build failed"
        exit 1
    }
    
    Write-Info "Image built successfully"
}

function Test-Image {
    Write-Info "Testing Docker image..."
    
    # Start container
    $ContainerId = docker run -d `
        -p 8000:8000 `
        -e AWS_REGION=us-east-1 `
        -e DEV_MODE=dev `
        --name "test-${ImageName}" `
        "${ImageName}:${Version}"
    
    Write-Info "Container started: $($ContainerId.Substring(0,12))"
    
    # Wait for startup
    Start-Sleep -Seconds 5
    
    # Health check
    try {
        $response = Invoke-WebRequest -Uri http://localhost:8000/docs -UseBasicParsing
        Write-Info "Health check passed"
    }
    catch {
        Write-Error "Health check failed"
        docker logs $ContainerId
        docker rm -f $ContainerId
        exit 1
    }
    
    # Cleanup
    docker rm -f $ContainerId | Out-Null
    Write-Info "Test completed successfully"
}

function Push-Image {
    if ([string]::IsNullOrEmpty($Registry)) {
        Write-Warn "No registry specified, skipping push"
        return
    }
    
    Write-Info "Pushing to registry: $Registry"
    
    docker tag "${ImageName}:${Version}" "${Registry}/${ImageName}:${Version}"
    docker tag "${ImageName}:${Version}" "${Registry}/${ImageName}:latest"
    
    docker push "${Registry}/${ImageName}:${Version}"
    docker push "${Registry}/${ImageName}:latest"
    
    Write-Info "Images pushed successfully"
}

function Start-Container {
    Write-Info "Starting container..."
    
    docker compose up -d api
    
    Write-Info "Container started. View logs with: docker compose logs -f api"
    Write-Info "API docs available at: http://localhost:8000/docs"
}

function Remove-Resources {
    Write-Info "Cleaning up..."
    
    docker compose down -v
    docker rmi "${ImageName}:${Version}" "${ImageName}:latest" 2>$null
    
    Write-Info "Cleanup completed"
}

function Show-Usage {
    @"
Docker Build & Deploy Script for Data Analyst Backend

USAGE:
    .\docker-build.ps1 [OPTIONS] COMMAND

COMMANDS:
    build       Build Docker image
    test        Build and test image
    push        Build, test, and push to registry
    run         Run container locally
    clean       Remove local images and containers
    help        Show this help message

OPTIONS:
    -Version <version>      Set image version (default: latest)
    -Registry <url>         Set Docker registry URL
    -Help                   Show this help message

EXAMPLES:
    # Build image
    .\docker-build.ps1 build

    # Build with custom version
    .\docker-build.ps1 -Version 1.0.0 build

    # Build, test, and push to ECR
    .\docker-build.ps1 -Registry 123456789012.dkr.ecr.us-east-1.amazonaws.com -Version 1.0.0 push

    # Run locally
    .\docker-build.ps1 run

    # Clean up
    .\docker-build.ps1 clean
"@
}

# Main
if ($Help -or $Command -eq 'help') {
    Show-Usage
    exit 0
}

switch ($Command) {
    'build' {
        Test-Prerequisites
        Build-Image
    }
    'test' {
        Test-Prerequisites
        Build-Image
        Test-Image
    }
    'push' {
        Test-Prerequisites
        Build-Image
        Test-Image
        Push-Image
    }
    'run' {
        Start-Container
    }
    'clean' {
        Remove-Resources
    }
    default {
        Show-Usage
        exit 1
    }
}

Write-Info "Done!"
