# SSL Certificate Setup for Multiple Pure Bhakti Applications

This document explains how to set up SSL certificates for multiple applications running in parallel.

## Current Setup

The **purebhakti_apis** application is running on:
- HTTP: `http://localhost:8080` (redirects to HTTPS)
- HTTPS: `https://localhost:8443`

## For Frontend Applications

### Option 1: Use Different Ports (Recommended)
Configure your frontend app to use different ports:
- Frontend HTTP: `http://localhost:80`
- Frontend HTTPS: `https://localhost:443`
- API HTTPS: `https://localhost:8443`

### Option 2: Share SSL Certificates

1. **Run the setup script** from your frontend app directory:
   ```bash
   ../purebhakti_apis/setup-shared-ssl.sh
   ```

2. **Update docker-compose.prod.yml** to mount certificates:
   ```yaml
   nginx:
     volumes:
       - ./ssl/certbot/conf:/etc/letsencrypt:ro
       - ./ssl/certbot/www:/var/www/certbot:ro
   ```

3. **Configure nginx** to use the certificates:
   ```nginx
   ssl_certificate /etc/letsencrypt/live/purebhaktibase.com/fullchain.pem;
   ssl_certificate_key /etc/letsencrypt/live/purebhaktibase.com/privkey.pem;
   ```

### Option 3: Generate New Certificates

For different subdomains (e.g., `app.purebhaktibase.com`, `api.purebhaktibase.com`):

1. **Create certificate directories:**
   ```bash
   mkdir -p ./ssl/certbot/conf ./ssl/certbot/www
   ```

2. **Generate certificates with Docker:**
   ```bash
   docker run --rm \
     -v ./ssl/certbot/conf:/etc/letsencrypt \
     -v ./ssl/certbot/www:/var/www/certbot \
     certbot/certbot certonly \
     --webroot --webroot-path=/var/www/certbot \
     --email your-email@domain.com \
     --agree-tos --no-eff-email \
     -d your-subdomain.purebhaktibase.com
   ```

## Port Allocation Strategy

| Application | HTTP Port | HTTPS Port | Access URL |
|-------------|-----------|------------|------------|
| API         | 8080      | 8443       | `https://localhost:8443` |
| Frontend    | 80        | 443        | `https://localhost` |

⚠️  **Important**: If frontend is already configured for port 443, no conflict exists, but:
- Frontend must call API at port 8443: `https://localhost:8443/api/v1`
- Update frontend environment variables to point to the correct API port
- Ensure CORS allows frontend domain → API domain requests

## Quick Commands

```bash
# Copy SSL certificates to frontend app
cd ../your-frontend-app
../purebhakti_apis/setup-shared-ssl.sh

# Deploy with SSL
docker-compose -f docker-compose.prod.yml up --build -d

# Check certificate validity
openssl x509 -in ./ssl/certbot/conf/live/purebhaktibase.com/fullchain.pem -text -noout
```

## Troubleshooting

- **Certificate not found**: Run the setup script first
- **Permission denied**: Ensure Docker has access to SSL directories
- **Port conflict**: Use different ports for each application
- **SSL handshake failed**: Check certificate validity and paths

## Security Notes

- Never commit private keys to version control
- Use `.gitignore` to exclude `ssl/` directories
- Rotate certificates regularly (Let's Encrypt auto-renews every 90 days)
- Use environment variables for sensitive configuration