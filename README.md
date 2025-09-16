# Pure Bhakti Vault API

A RESTful API for Pure Bhakti spiritual content including books, articles, lectures, and verses.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs with Python
- **PostgreSQL Database**: Robust relational database for storing spiritual content
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **SSL/HTTPS**: Production-ready SSL configuration
- **CORS Support**: Multi-platform support for web and mobile applications
- **API Documentation**: Auto-generated interactive API docs with Swagger UI

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Docker (optional, for containerized deployment)

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd purebhakti_apis
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Deployment

For Docker deployment instructions, see [DOCKER_README.md](DOCKER_README.md).

## API Endpoints

### Books
- `GET /api/v1/books` - List all books
- `GET /api/v1/books/{book_id}` - Get specific book details

### Content
- `GET /api/v1/content` - List content with filtering
- `GET /api/v1/content/{content_id}` - Get specific content

### Glossary
- `GET /api/v1/glossary` - List glossary terms
- `GET /api/v1/glossary/{term_id}` - Get specific term

### Page Maps
- `GET /api/v1/pages` - Get page mapping information

## Project Structure

```
purebhakti_apis/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration settings
│   ├── database.py       # Database connection
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── routers/          # API route definitions
│   └── services/         # Business logic
├── ssl/                  # SSL certificates (production)
├── nginx/                # Nginx configuration
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Docker image definition
├── requirements.txt     # Python dependencies
└── main.py             # Application entry point
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database_name

# Application Settings
ENVIRONMENT=development
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Documentation

- [Docker Deployment Guide](DOCKER_README.md)
- [Production Deployment](PRODUCTION_DEPLOYMENT.md)
- [SSL Setup Guide](SSL_SETUP.md)
- [React Integration](REACT_INTEGRATION.md)
- [Production SSL Configuration](PRODUCTION_SSL.md)

## Development

### Running Tests
```bash
# Add test framework if needed
pytest
```

### Code Style
```bash
# Add linting tools if needed
flake8 app/
black app/
```

## Production Deployment

For production deployment with SSL and proper security configuration, see:
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
- [SSL_SETUP.md](SSL_SETUP.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For questions or support, please [create an issue](../../issues) or contact the development team.