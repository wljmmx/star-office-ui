#!/bin/bash
# Star Office UI - Environment Setup Script
# This script generates secure keys and creates .env file

set -e

echo "🔐 Star Office UI - Environment Setup"
echo "======================================"
echo ""

# Generate FLASK_SECRET_KEY
FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "✅ Generated FLASK_SECRET_KEY"

# Generate JWT_SECRET_KEY
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "✅ Generated JWT_SECRET_KEY"

# Create .env file from template
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Star Office UI - Environment Configuration
# Generated on $(date)

# ===========================================
# Flask Configuration
# ===========================================
FLASK_SECRET_KEY=$FLASK_SECRET_KEY

# Debug mode: true for development, false for production
SOUI_DEBUG=true

# ===========================================
# Server Configuration
# ===========================================
SOUI_HOST=127.0.0.1
SOUI_PORT=5000

# ===========================================
# CORS Configuration
# ===========================================
SOUI_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ===========================================
# JWT Authentication Configuration
# ===========================================
JWT_SECRET_KEY=$JWT_SECRET_KEY

# ===========================================
# WebSocket/Sync Configuration
# ===========================================
SOUI_SYNC_INTERVAL=5

# ===========================================
# Database Configuration
# ===========================================
SOUI_DATABASE_PATH=./backend/skills/github-collab/github-collab.db

# ===========================================
# Security Configuration
# ===========================================
SOUI_COOKIE_SECURE=false

# ===========================================
# Logging Configuration
# ===========================================
SOUI_LOG_LEVEL=DEBUG

# ===========================================
# Frontend Configuration
# ===========================================
SOUI_FRONTEND_DIR=./frontend
EOF
    echo "✅ Created .env file"
else
    echo "⚠️  .env file already exists, skipping creation"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review .env file and adjust settings as needed"
echo "2. Install dependencies: pip install -r backend/requirements.txt"
echo "3. Initialize database: python backend/init_db.py"
echo "4. Run the application: python backend/main.py"
echo ""
echo "🔑 Your generated keys:"
echo "   FLASK_SECRET_KEY: $FLASK_SECRET_KEY"
echo "   JWT_SECRET_KEY: $JWT_SECRET_KEY"
echo ""
echo "⚠️  IMPORTANT: Keep these keys secure! Never commit .env to version control."
echo ""
