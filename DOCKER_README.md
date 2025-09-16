# Docker Deployment Guide

This guide explains how to deploy the Pure Bhakti APIs using Docker and Docker Compose.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   cd /Users/kamaldivi/Development/Python/purebhakti_apis
   ```

2. **Build and start the services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the API**:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Services

### FastAPI Application (api)
- **Port**: 8000
- **Health Check**: http://localhost:8000/health
- **Environment Variables**:
  - `DATABASE_URL`: Complete PostgreSQL connection string
  - `DATABASE_HOST`: Database host (default: db)
  - `DATABASE_PORT`: Database port (default: 5432)
  - `DATABASE_NAME`: Database name (default: purebhakti_db)
  - `DATABASE_USER`: Database user (default: purebhakti_user)
  - `DATABASE_PASSWORD`: Database password (default: purebhakti_password)

### PostgreSQL Database (db)
- **Port**: 5432 (exposed on host)
- **Database**: purebhakti_db
- **User**: purebhakti_user
- **Password**: purebhakti_password
- **Data Persistence**: Named volume `postgres_data`

## Available Commands

### Start services in background
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop services and remove volumes (WARNING: This will delete all data)
```bash
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs api
docker-compose logs db
```

### Rebuild and restart services
```bash
docker-compose up --build --force-recreate
```

### Access database directly
```bash
docker-compose exec db psql -U purebhakti_user -d purebhakti_db
```

### Execute commands in API container
```bash
docker-compose exec api bash
```

## Environment Variables

You can create a `.env` file to override default environment variables:

```bash
cp .env.example .env
# Edit .env with your preferred values
```

## Database Initialization

The database is automatically initialized with the schema from `db/create_tables.sql` when the PostgreSQL container starts for the first time.

## Health Checks

Both services include health checks:
- **API**: Checks if the application responds to HTTP requests
- **Database**: Checks if PostgreSQL is ready to accept connections

## Troubleshooting

### Check service status
```bash
docker-compose ps
```

### Check if database is ready
```bash
docker-compose exec db pg_isready -U purebhakti_user -d purebhakti_db
```

### Reset everything (WARNING: This will delete all data)
```bash
docker-compose down -v
docker system prune -f
docker-compose up --build
```

### Common Issues

1. **Port already in use**: Change the ports in `docker-compose.yml`
2. **Permission denied**: Ensure Docker daemon is running
3. **Database connection failed**: Wait for database health check to pass
4. **Build fails**: Check Docker daemon and network connectivity

## Production Considerations

For production deployment, consider:

1. **Environment Variables**: Use proper secrets management
2. **CORS**: Configure allowed origins in `app/main.py`
3. **Database**: Use managed PostgreSQL service or proper backup strategy
4. **Reverse Proxy**: Use nginx or similar for SSL termination
5. **Resource Limits**: Add resource constraints to docker-compose.yml
6. **Logging**: Configure proper log aggregation
7. **Monitoring**: Add monitoring and alerting

## API Endpoints

Once running, the following endpoints are available:

- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `GET /api/v1/books` - List books with pagination
- `GET /api/v1/books/{book_id}` - Get specific book
- `GET /api/v1/books/{book_id}/content/{page_number}` - Get page content
- `GET /api/v1/books/{book_id}/content` - Get book content with pagination
- `GET /api/v1/books/{book_id}/glossary` - Get book glossary terms
- `GET /api/v1/books/{book_id}/glossary/{term}` - Get specific glossary term
- `GET /api/v1/books/{book_id}/pages/core` - Get core pages for a book
- `GET /api/v1/books/{book_id}/pages` - Get full page map for a book
- `GET /api/v1/glossary/search` - Search glossary terms across books