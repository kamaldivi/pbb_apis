# SSL Setup Guide

## 🔒 SSL/HTTPS Configuration Complete

Your FastAPI application now supports SSL/HTTPS with nginx as a reverse proxy.

## 📁 Files Added

### SSL Certificates
- `ssl/certificate.crt` - Self-signed SSL certificate (365 days)
- `ssl/private.key` - Private key for SSL certificate

### Nginx Configuration
- `nginx/nginx.conf` - Nginx reverse proxy with SSL termination

### Updated Files
- `docker-compose.yml` - Added nginx service with SSL configuration

## 🌐 Access Points

### HTTPS (Secure) - Port 8443
- **API**: https://localhost:8443
- **Health Check**: https://localhost:8443/health
- **API Documentation**: https://localhost:8443/docs
- **ReDoc**: https://localhost:8443/redoc
- **API Endpoints**: https://localhost:8443/api/v1/...

### HTTP (Redirects to HTTPS) - Port 8080
- **Any HTTP request**: http://localhost:8080 -> redirects to https://localhost:8443

## 🔧 Configuration Features

### Security
- ✅ **TLS 1.2 & 1.3** support
- ✅ **Modern cipher suites**
- ✅ **Security headers** (HSTS, X-Frame-Options, etc.)
- ✅ **Automatic HTTP to HTTPS redirect**

### Performance
- ✅ **Gzip compression** for JSON/JS/CSS
- ✅ **HTTP/2** support
- ✅ **SSL session caching**
- ✅ **Proxy buffering optimization**

### Monitoring
- ✅ **Health checks** for both nginx and API
- ✅ **Proper dependency management**
- ✅ **Graceful restarts**

## 🚀 Usage

```bash
# Start SSL-enabled services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs nginx
docker-compose logs api

# Stop services
docker-compose down
```

## 🧪 Testing SSL

```bash
# Test HTTPS endpoint
curl -k https://localhost:8443/health

# Test HTTP redirect
curl -I http://localhost:8080/health

# Test API over HTTPS
curl -k https://localhost:8443/api/v1/books?page=1&size=1

# Test with certificate verification (will fail with self-signed)
curl https://localhost:8443/health  # Will show certificate error
```

## 🔑 Certificate Information

**Current Setup**: Self-signed certificate for localhost
- **Valid for**: 365 days
- **Subject**: CN=localhost
- **Key Length**: 4096 bits

## 🚨 Browser Security Warning

Since this uses a self-signed certificate, browsers will show a security warning. For local development:
1. Click "Advanced"
2. Click "Proceed to localhost (unsafe)"
3. Or add certificate to trusted store

## 🌟 Production Considerations

For production deployment, consider:

1. **Real SSL Certificate**:
   - Use Let's Encrypt with certbot
   - Purchase from a trusted CA
   - Use wildcard certificates for subdomains

2. **Domain Configuration**:
   - Update `server_name` in nginx.conf
   - Update certificate CN/SAN fields
   - Configure proper DNS

3. **Enhanced Security**:
   - Enable OCSP stapling
   - Add certificate transparency monitoring
   - Implement rate limiting
   - Add WAF protection

## 📋 Architecture

```
Internet → nginx:443 (SSL termination) → api:8000 (HTTP internal)
         ↳ nginx:80 (HTTP redirect to HTTPS)
```

The nginx container handles:
- SSL/TLS termination
- HTTP to HTTPS redirects
- Security headers
- Gzip compression
- Reverse proxy to FastAPI

The API container remains unchanged and communicates internally via HTTP.