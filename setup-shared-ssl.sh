#!/bin/bash

# SSL Certificate Setup Script for Pure Bhakti Applications
# Run this script in any app directory that needs SSL certificates

APP_NAME=$(basename "$PWD")
echo "🔒 Setting up SSL certificates for $APP_NAME..."

# Check if we have source certificates
if [ -f "../purebhakti_apis/ssl/purebhaktibase.com.crt" ]; then
    echo "📋 Found source certificates in purebhakti_apis"

    # Create directory structure
    mkdir -p ./ssl/certbot/conf/live/purebhaktibase.com
    mkdir -p ./ssl/certbot/www

    # Copy certificates to Let's Encrypt format
    cp ../purebhakti_apis/ssl/purebhaktibase.com.crt ./ssl/certbot/conf/live/purebhaktibase.com/fullchain.pem
    cp ../purebhakti_apis/ssl/purebhaktibase.com.key ./ssl/certbot/conf/live/purebhaktibase.com/privkey.pem

    echo "✅ SSL certificates copied successfully!"
    echo "📁 Certificates available at: ./ssl/certbot/conf/live/purebhaktibase.com/"

elif [ -f "../purebhakti_apis/ssl/certbot/conf/live/purebhaktibase.com/fullchain.pem" ]; then
    echo "📋 Found Let's Encrypt format certificates"

    # Create directory structure
    mkdir -p ./ssl/certbot/conf/live/purebhaktibase.com
    mkdir -p ./ssl/certbot/www

    # Copy Let's Encrypt certificates
    cp ../purebhakti_apis/ssl/certbot/conf/live/purebhaktibase.com/* ./ssl/certbot/conf/live/purebhaktibase.com/

    echo "✅ Let's Encrypt certificates copied successfully!"

else
    echo "❌ No SSL certificates found in ../purebhakti_apis/ssl/"
    echo "📋 Available options:"
    echo "   1. Copy your certificates to ../purebhakti_apis/ssl/ as:"
    echo "      - purebhaktibase.com.crt (certificate)"
    echo "      - purebhaktibase.com.key (private key)"
    echo "   2. Generate new certificates with certbot"
    echo "   3. Use staging/development mode without SSL"
    exit 1
fi

echo ""
echo "🌐 Next steps:"
echo "   • Update docker-compose.prod.yml to mount SSL certificates"
echo "   • Configure nginx to use the certificates"
echo "   • Deploy with: docker-compose -f docker-compose.prod.yml up -d"
echo ""