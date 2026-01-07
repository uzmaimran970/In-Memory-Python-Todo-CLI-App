#!/bin/bash
# Railway Deployment Script - Run this in the SAME terminal where you did "railway login"

set -e

echo "🚀 Starting Railway Deployment..."
cd /mnt/c/Users/pc/Desktop/todo_hackathon2/backend

# Initialize project
echo "📦 Initializing Railway project..."
railway init --name todo-backend-production

# Set environment variables
echo "⚙️  Setting environment variables..."
railway variables set DATABASE_URL="postgresql://neondb_owner:npg_fjZJF8XEs5dv@ep-patient-king-a1eko8at-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
railway variables set BETTER_AUTH_SECRET="9eb4ea939ffbae7e084c9432d41fe55921f786164ba326c7a2070cf75fca58c6"

# Deploy
echo "🚀 Deploying..."
railway up

# Generate domain
echo "🌐 Generating domain..."
railway domain

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "Run 'railway status' to see your live URL"
