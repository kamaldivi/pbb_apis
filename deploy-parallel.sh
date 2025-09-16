#!/bin/bash

# Script to deploy multiple Pure Bhakti applications in parallel
# This script manages networking and port allocation for multiple apps

echo "🚀 Setting up parallel deployment for Pure Bhakti applications..."

# Create shared network if it doesn't exist
if ! docker network ls | grep -q "purebhakti_shared"; then
    echo "📡 Creating shared network: purebhakti_shared"
    docker network create purebhakti_shared
else
    echo "📡 Using existing network: purebhakti_shared"
fi

# Function to deploy an application
deploy_app() {
    local app_path=$1
    local app_name=$2
    local compose_file=$3

    echo "🔧 Deploying $app_name from $app_path..."

    if [ -d "$app_path" ]; then
        cd "$app_path"
        docker-compose -f "$compose_file" down 2>/dev/null || true
        docker-compose -f "$compose_file" up --build -d
        cd - > /dev/null
        echo "✅ $app_name deployed successfully"
    else
        echo "❌ Directory $app_path not found"
    fi
}

# Deploy API application (this one) on ports 8080/8443
echo "🔧 Deploying Pure Bhakti APIs..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
docker-compose -f docker-compose.prod.yml up --build -d

# Check if frontend app exists and deploy it
FRONTEND_PATH="../pbb-test-bed"  # Adjust this path as needed
if [ -d "$FRONTEND_PATH" ]; then
    echo "🔧 Found frontend application at $FRONTEND_PATH"
    echo "⚠️  Make sure the frontend app uses ports 80/443 or different ports"
    echo "⚠️  Frontend should be configured to connect to API at port 8080"
    # Uncomment the next line if you want to auto-deploy the frontend too
    # deploy_app "$FRONTEND_PATH" "Frontend App" "docker-compose.prod.yml"
else
    echo "ℹ️  Frontend app not found at $FRONTEND_PATH"
fi

echo "📊 Current container status:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"

echo ""
echo "🌐 Access URLs:"
echo "  • API: http://localhost:8080"
echo "  • API SSL: https://localhost:8443"
echo "  • Frontend: http://localhost:80 (if deployed separately)"
echo ""
echo "✨ Parallel deployment complete!"