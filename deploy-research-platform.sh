#!/bin/bash
set -e

echo "🚀 Mayan EDMS Research Platform Deployment"
echo "=========================================="

# Function to print colored output
print_status() {
    echo -e "\033[1;32m$1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m$1\033[0m"
}

print_error() {
    echo -e "\033[1;31m$1\033[0m"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Stop any existing containers
print_status "🛑 Stopping existing containers..."
docker-compose -f docker-compose.research-platform.yml down

# Remove old research platform image to ensure fresh build
print_status "🗑️  Removing old images..."
docker rmi mayan-research-platform:latest 2>/dev/null || true

# Build the research platform image
print_status "🔨 Building Mayan EDMS Research Platform..."
docker-compose -f docker-compose.research-platform.yml build --no-cache

# Start the services
print_status "🚀 Starting Research Platform services..."
docker-compose -f docker-compose.research-platform.yml up -d

# Wait for services to be ready
print_status "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
print_status "🔍 Checking service status..."
docker-compose -f docker-compose.research-platform.yml ps

# Test if the research platform is accessible
print_status "🧪 Testing Research Platform..."
if curl -f -s http://localhost:8080/admin/ > /dev/null; then
    print_status "✅ Research Platform is accessible at http://localhost:8080"
    print_status "🎯 Admin interface: http://localhost:8080/admin/"
    print_status "📊 Research features should be available in the admin interface"
else
    print_warning "⚠️  Platform may still be starting up. Please wait a few more minutes."
fi

# Show logs for troubleshooting
print_status "📋 Recent logs (press Ctrl+C to stop following):"
echo "To follow logs: docker-compose -f docker-compose.research-platform.yml logs -f"
echo "To access shell: docker-compose -f docker-compose.research-platform.yml exec app /bin/bash"
echo ""

# Follow logs
docker-compose -f docker-compose.research-platform.yml logs -f app 