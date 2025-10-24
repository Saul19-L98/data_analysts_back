#!/bin/bash
# =============================================================================
# Docker Build & Deploy Script for Data Analyst Backend
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="data-analyst-back"
VERSION="${VERSION:-latest}"
REGISTRY="${REGISTRY:-}"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker buildx version &> /dev/null; then
        log_warn "Docker BuildKit not available, using standard build"
    fi
    
    log_info "Prerequisites check passed"
}

# Build image
build_image() {
    log_info "Building Docker image: ${IMAGE_NAME}:${VERSION}"
    
    export DOCKER_BUILDKIT=1
    
    docker build \
        --tag "${IMAGE_NAME}:${VERSION}" \
        --tag "${IMAGE_NAME}:latest" \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        .
    
    log_info "Image built successfully"
}

# Test image
test_image() {
    log_info "Testing Docker image..."
    
    # Start container
    CONTAINER_ID=$(docker run -d \
        -p 8000:8000 \
        -e AWS_REGION=us-east-1 \
        -e DEV_MODE=dev \
        --name test-${IMAGE_NAME} \
        "${IMAGE_NAME}:${VERSION}")
    
    log_info "Container started: ${CONTAINER_ID:0:12}"
    
    # Wait for startup
    sleep 5
    
    # Health check
    if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
        log_info "Health check passed"
    else
        log_error "Health check failed"
        docker logs "${CONTAINER_ID}"
        docker rm -f "${CONTAINER_ID}"
        exit 1
    fi
    
    # Cleanup
    docker rm -f "${CONTAINER_ID}"
    log_info "Test completed successfully"
}

# Push to registry
push_image() {
    if [ -z "${REGISTRY}" ]; then
        log_warn "No registry specified, skipping push"
        return
    fi
    
    log_info "Pushing to registry: ${REGISTRY}"
    
    docker tag "${IMAGE_NAME}:${VERSION}" "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    docker tag "${IMAGE_NAME}:${VERSION}" "${REGISTRY}/${IMAGE_NAME}:latest"
    
    docker push "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    docker push "${REGISTRY}/${IMAGE_NAME}:latest"
    
    log_info "Images pushed successfully"
}

# Show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] COMMAND

Commands:
    build       Build Docker image
    test        Build and test image
    push        Build, test, and push to registry
    run         Run container locally
    clean       Remove local images and containers

Options:
    -v VERSION  Set image version (default: latest)
    -r REGISTRY Set Docker registry URL
    -h          Show this help message

Examples:
    # Build image
    $0 build

    # Build with custom version
    $0 -v 1.0.0 build

    # Build, test, and push to ECR
    $0 -r 123456789012.dkr.ecr.us-east-1.amazonaws.com -v 1.0.0 push

    # Run locally
    $0 run

EOF
}

# Run container
run_container() {
    log_info "Starting container..."
    
    docker compose up -d api
    
    log_info "Container started. View logs with: docker compose logs -f api"
    log_info "API docs available at: http://localhost:8000/docs"
}

# Clean up
clean() {
    log_info "Cleaning up..."
    
    docker compose down -v
    docker rmi "${IMAGE_NAME}:${VERSION}" "${IMAGE_NAME}:latest" 2>/dev/null || true
    
    log_info "Cleanup completed"
}

# Parse arguments
while getopts "v:r:h" opt; do
    case $opt in
        v) VERSION="$OPTARG" ;;
        r) REGISTRY="$OPTARG" ;;
        h) show_usage; exit 0 ;;
        *) show_usage; exit 1 ;;
    esac
done
shift $((OPTIND-1))

# Main
case "${1:-}" in
    build)
        check_prerequisites
        build_image
        ;;
    test)
        check_prerequisites
        build_image
        test_image
        ;;
    push)
        check_prerequisites
        build_image
        test_image
        push_image
        ;;
    run)
        run_container
        ;;
    clean)
        clean
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

log_info "Done!"
