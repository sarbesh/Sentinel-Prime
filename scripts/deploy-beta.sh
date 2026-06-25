#!/bin/bash
# Sentinel Prime Beta Deployment Script
# One-line deployment for beta testers

set -e

echo "🚀 Sentinel Prime Beta Deployment"
echo "=================================="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   curl -fsSL https://get.docker.com | sh"
    exit 1
fi

echo "✅ Docker found: $(docker --version)"

# Clone or update repository
if [ -d "sentinel-prime" ]; then
    echo "📦 Updating existing installation..."
    cd sentinel-prime
    git pull
else
    echo "📦 Cloning repository..."
    git clone https://github.com/your-org/sentinel-prime.git
    cd sentinel-prime
fi

# Create data directory
mkdir -p data logs

# Deploy with Docker
echo "🐳 Starting services..."
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 10

# Health check
echo "🏥 Running health checks..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API: OK"
else
    echo "⚠️  Backend API: Not responding (may need more time)"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Web UI: OK"
else
    echo "⚠️  Web UI: Not responding (may need more time)"
fi

echo ""
echo "=================================="
echo "🎉 Deployment Complete!"
echo ""
echo "Access the dashboard:"
echo "  👉 http://localhost:3000"
echo ""
echo "First steps:"
echo "  1. Open the dashboard in your browser"
echo "  2. Go to 'Devices' to see detected devices"
echo "  3. Click 'Scans' → 'New Scan' to run your first scan"
echo "  4. Monitor 'Dashboard' for network activity"
echo ""
echo "Useful commands:"
echo "  View logs:     docker-compose logs -f"
echo "  Stop:          docker-compose down"
echo "  Restart:       docker-compose restart"
echo "  Status:        docker-compose ps"
echo ""
echo "Need help?"
echo "  Documentation: https://github.com/your-org/sentinel-prime/blob/main/DEPLOYMENT_GUIDE.md"
echo "  Discord:       https://discord.gg/sentinel-prime"
echo "  Issues:        https://github.com/your-org/sentinel-prime/issues"
echo ""
echo "Welcome to Sentinel Prime Beta! 🛡️"
echo "=================================="
