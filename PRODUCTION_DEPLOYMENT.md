# 🚀 Production Deployment Guide - purebhaktibase.com

## Prerequisites

1. **Domain Configuration**
   - Domain: `purebhaktibase.com` with DNS pointing to your server
   - Server with public IP address
   - Ports 80 and 443 open on firewall

2. **Server Requirements**
   - Docker and Docker Compose installed
   - PostgreSQL database accessible
   - Git for code deployment

## Step-by-Step Deployment

### 1. Prepare Server Environment

```bash
# Clone repository
git clone <your-repo-url>
cd purebhakti_apis

# Create SSL directories
mkdir -p ssl/certbot/conf ssl/certbot/www

# Verify database connectivity
docker run --rm postgres:15 psql "postgresql://pbbdbuser:Govinda2025%23@host.docker.internal:5432/pure_bhakti_vault" -c "SELECT 1;"
```

### 2. Initial SSL Certificate Setup

```bash
# Start nginx for Let's Encrypt challenge (HTTP only first)
# Temporarily modify nginx-prod.conf to comment out SSL lines
docker-compose -f docker-compose.prod.yml up nginx -d

# Request SSL certificate
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --email your-email@purebhaktibase.com \
  --agree-tos \
  --no-eff-email \
  -d purebhaktibase.com \
  -d www.purebhaktibase.com

# Verify certificate creation
ls -la ssl/certbot/conf/live/purebhaktibase.com/
```

### 3. Deploy Production Services

```bash
# Stop temporary services
docker-compose -f docker-compose.prod.yml down

# Start full production stack
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

### 4. Verify Deployment

```bash
# Test health endpoint
curl https://purebhaktibase.com/health

# Test API endpoint
curl https://purebhaktibase.com/api/v1/books?page=1&size=1

# Check SSL certificate
curl -I https://purebhaktibase.com/

# Test HTTP redirect
curl -I http://purebhaktibase.com/
```

### 5. Monitor and Maintain

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f api

# Test certificate renewal
docker-compose -f docker-compose.prod.yml run --rm certbot renew --dry-run

# Restart services if needed
docker-compose -f docker-compose.prod.yml restart
```

## Environment Variables (Production)

Create `.env.prod` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://pbbdbuser:Govinda2025%23@host.docker.internal:5432/pure_bhakti_vault
DB_HOST=host.docker.internal
DB_PORT=5432
DB_NAME=pure_bhakti_vault
DB_USER=pbbdbuser
DB_PASSWORD=Govinda2025#

# Environment
ENVIRONMENT=production

# CORS Origins (production domains)
CORS_ORIGINS=https://www.purebhaktibase.com,https://purebhaktibase.com,https://api.purebhaktibase.com,https://app.purebhaktibase.com
```

## API Endpoints (Production)

- **Base URL**: `https://purebhaktibase.com`
- **Health Check**: `https://purebhaktibase.com/health`
- **API Documentation**: `https://purebhaktibase.com/docs`
- **ReDoc**: `https://purebhaktibase.com/redoc`
- **Books API**: `https://purebhaktibase.com/api/v1/books`

## Security Features

✅ **SSL/TLS Encryption** with Let's Encrypt certificates
✅ **HSTS Headers** for enhanced security
✅ **Modern Cipher Suites** (TLS 1.2/1.3)
✅ **Security Headers** (XSS protection, content type sniffing protection)
✅ **CORS Configuration** for specific domains only
✅ **HTTP to HTTPS Redirects**
✅ **Automated Certificate Renewal**

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker exec -t postgres_container pg_dump -U pbbdbuser pure_bhakti_vault > backup_$(date +%Y%m%d).sql

# Restore backup
docker exec -i postgres_container psql -U pbbdbuser pure_bhakti_vault < backup_20240315.sql
```

### Application Backup

```bash
# Backup certificates
tar -czf ssl_backup_$(date +%Y%m%d).tar.gz ssl/

# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz nginx/ docker-compose.prod.yml
```

## Troubleshooting

### SSL Certificate Issues

```bash
# Check certificate expiry
docker-compose -f docker-compose.prod.yml run --rm certbot certificates

# Force renewal
docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal

# Check nginx SSL configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

### Database Connection Issues

```bash
# Test database connection from API container
docker-compose -f docker-compose.prod.yml exec api python -c "
from app.database import engine
try:
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

### Service Health Checks

```bash
# Check all container health
docker-compose -f docker-compose.prod.yml ps

# View container logs
docker-compose -f docker-compose.prod.yml logs api
docker-compose -f docker-compose.prod.yml logs nginx
```

## Performance Optimization

### Nginx Optimization

- **Gzip Compression**: Enabled for JSON, JS, CSS
- **HTTP/2**: Enabled for faster multiplexing
- **SSL Session Caching**: 10m cache for better performance
- **Proxy Buffering**: Optimized for API responses

### Database Optimization

- **Connection Pooling**: FastAPI with SQLAlchemy
- **Query Optimization**: Proper indexing on frequently queried fields
- **Pagination**: All list endpoints support pagination

## Monitoring and Alerts

### Health Checks

All services include health checks:
- **API**: HTTP health endpoint check
- **Nginx**: Configuration validation
- **Database**: Connection tests

### Log Monitoring

```bash
# Real-time log monitoring
docker-compose -f docker-compose.prod.yml logs -f --tail=100

# Error log filtering
docker-compose -f docker-compose.prod.yml logs | grep -i error
```

## Scaling Considerations

### Horizontal Scaling

To scale the API:

```bash
# Scale API containers
docker-compose -f docker-compose.prod.yml up -d --scale api=3

# Update nginx upstream configuration for load balancing
```

### Database Scaling

Consider:
- Read replicas for improved performance
- Connection pooling optimization
- Database indexing review

## SSL Certificate Renewal

The certbot container automatically renews certificates every 12 hours. Manual renewal:

```bash
# Test renewal (dry run)
docker-compose -f docker-compose.prod.yml run --rm certbot renew --dry-run

# Force renewal
docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal

# Reload nginx after renewal
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

## Final Checklist

- [ ] Domain DNS points to server IP
- [ ] SSL certificates obtained and valid
- [ ] Database connectivity verified
- [ ] All services running and healthy
- [ ] API endpoints responding correctly
- [ ] CORS configured for production domains
- [ ] Monitoring and logging operational
- [ ] Backup procedures in place
- [ ] Certificate auto-renewal tested

Your Pure Bhakti API is now production-ready at `https://purebhaktibase.com`!