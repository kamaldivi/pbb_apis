# 🔒 Production SSL Setup Guide

## FREE SSL Certificates with Let's Encrypt

Yes! You can get **FREE SSL certificates** that are trusted by all browsers using Let's Encrypt. Here's how:

## Option 1: Automated Let's Encrypt with Certbot (Recommended)

### 1. Create Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
services:
  api:
    build: .
    restart: unless-stopped
    environment:
      # Update with your production database
      - DATABASE_URL=postgresql://user:password@your-db-host:5432/database
      - DB_HOST=your-db-host
      - DB_PORT=5432
      - DB_NAME=database
      - DB_USER=user
      - DB_PASSWORD=password
    expose:
      - "8000"
    volumes:
      - ./app:/app/app:ro

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx-prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl/certbot/conf:/etc/letsencrypt:ro
      - ./ssl/certbot/www:/var/www/certbot:ro
    depends_on:
      - api

  certbot:
    image: certbot/certbot
    restart: "no"
    volumes:
      - ./ssl/certbot/conf:/etc/letsencrypt
      - ./ssl/certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

### 2. Create Production Nginx Config

Create `nginx/nginx-prod.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    # HTTP server - Let's Encrypt challenges + redirect
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;

        # Let's Encrypt challenge location
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # Redirect all other HTTP requests to HTTPS
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # Let's Encrypt SSL certificates
        ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

        # Modern SSL configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";

        # Proxy to API
        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 3. Initial Certificate Request

```bash
# Create directories
mkdir -p ssl/certbot/conf ssl/certbot/www

# Start nginx without SSL first
docker-compose -f docker-compose.prod.yml up nginx -d

# Request initial certificate
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d yourdomain.com \
  -d www.yourdomain.com

# Restart nginx with SSL
docker-compose -f docker-compose.prod.yml restart nginx
```

### 4. Auto-Renewal Setup

The certbot container automatically renews certificates every 12 hours. To test renewal:

```bash
# Test renewal (dry run)
docker-compose -f docker-compose.prod.yml run --rm certbot renew --dry-run
```

## Option 2: Manual Certbot (Alternative)

If you prefer to run certbot manually on your server:

```bash
# Install certbot
sudo apt update
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates will be in /etc/letsencrypt/live/yourdomain.com/
# Copy them to your ssl/ directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/certificate.crt
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/private.key

# Set up auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Option 3: Cloudflare SSL (Free Tier)

If you use Cloudflare:

1. **Sign up** for Cloudflare (free)
2. **Add your domain** to Cloudflare
3. **Update nameservers** to Cloudflare's
4. **Enable SSL/TLS** in Cloudflare dashboard
5. **Set SSL mode** to "Full (strict)"
6. **Use Origin Certificates** for server-to-Cloudflare encryption

Benefits:
- Free SSL termination at edge
- DDoS protection
- CDN acceleration
- Easy setup

## Option 4: AWS Certificate Manager (If using AWS)

If deploying on AWS:

1. **Request certificate** in AWS Certificate Manager
2. **Validate domain** (DNS or email)
3. **Use with Application Load Balancer**
4. **Configure health checks**

Cost: FREE for AWS resources

## Domain Requirements

For any SSL certificate, you need:

1. **Registered domain** (GoDaddy, Namecheap, etc.)
2. **DNS control** (A record pointing to your server)
3. **Server with public IP**
4. **Port 80/443 accessible**

## Cost Comparison

| Method | Cost | Auto-Renewal | Trusted by Browsers |
|--------|------|--------------|-------------------|
| Let's Encrypt | FREE | ✅ Yes | ✅ Yes |
| Cloudflare | FREE | ✅ Yes | ✅ Yes |
| AWS ACM | FREE* | ✅ Yes | ✅ Yes |
| Commercial CA | $50-200/year | Manual | ✅ Yes |

*AWS ACM is free for AWS resources only

## 🚀 Recommended Approach

1. **Development**: Self-signed certificates (current setup)
2. **Production**: Let's Encrypt with automated renewal
3. **Enterprise**: Cloudflare or AWS ACM for additional features

## ⚡ Quick Start for Production

```bash
# 1. Update domain in nginx-prod.conf
sed -i 's/yourdomain.com/your-actual-domain.com/g' nginx/nginx-prod.conf

# 2. Get Let's Encrypt certificate
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path /var/www/certbot \
  --email your-email@domain.com --agree-tos --no-eff-email \
  -d your-actual-domain.com

# 3. Start production services
docker-compose -f docker-compose.prod.yml up -d
```

Let's Encrypt certificates are **completely free**, **automatically renewed**, and **trusted by all browsers**!