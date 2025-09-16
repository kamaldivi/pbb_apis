# 🔄 React Frontend Integration Guide

## Port Configuration for React + API

Your setup now supports both a React frontend and the API running simultaneously:

### Port Allocation
- **React Frontend**: `http://localhost:3000` (standard React port)
- **API HTTP**: `http://localhost:8080` → redirects to HTTPS
- **API HTTPS**: `https://localhost:8443` (secured API endpoints)

## React Environment Configuration

In your React app, create `.env.local`:

```bash
# Development API endpoint
REACT_APP_API_URL=https://localhost:8443

# Or for HTTP (will redirect to HTTPS)
# REACT_APP_API_URL=http://localhost:8080
```

## API Integration in React

### 1. Install Axios (recommended)
```bash
npm install axios
```

### 2. Create API client
```javascript
// src/api/client.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'https://localhost:8443',
  headers: {
    'Content-Type': 'application/json',
  },
  // For development with self-signed certificates
  httpsAgent: process.env.NODE_ENV === 'development' ?
    new (require('https').Agent)({ rejectUnauthorized: false }) : undefined
});

export default apiClient;
```

### 3. API service functions
```javascript
// src/api/books.js
import apiClient from './client';

export const booksAPI = {
  // Get all books with pagination
  getBooks: async (page = 1, size = 10) => {
    const response = await apiClient.get(`/api/v1/books?page=${page}&size=${size}`);
    return response.data;
  },

  // Get specific book
  getBook: async (bookId) => {
    const response = await apiClient.get(`/api/v1/books/${bookId}`);
    return response.data;
  },

  // Get book content
  getBookContent: async (bookId, page = 1, size = 10) => {
    const response = await apiClient.get(`/api/v1/books/${bookId}/content?page=${page}&size=${size}`);
    return response.data;
  },

  // Get page content
  getPageContent: async (bookId, pageNumber) => {
    const response = await apiClient.get(`/api/v1/books/${bookId}/content/${pageNumber}`);
    return response.data;
  },

  // Get glossary terms
  getGlossary: async (bookId, page = 1, size = 10) => {
    const response = await apiClient.get(`/api/v1/books/${bookId}/glossary?page=${page}&size=${size}`);
    return response.data;
  },

  // Search glossary
  searchGlossary: async (term, page = 1, size = 10) => {
    const response = await apiClient.get(`/api/v1/glossary/search?term=${term}&page=${page}&size=${size}`);
    return response.data;
  },

  // Get core pages
  getCorePages: async (bookId) => {
    const response = await apiClient.get(`/api/v1/books/${bookId}/pages/core`);
    return response.data;
  },

  // Get full page map
  getPageMap: async (bookId, page = 1, size = 50) => {
    const response = await apiClient.get(`/api/v1/books/${bookId}/pages?page=${page}&size=${size}`);
    return response.data;
  }
};
```

### 4. React Hook for API calls
```javascript
// src/hooks/useBooks.js
import { useState, useEffect } from 'react';
import { booksAPI } from '../api/books';

export const useBooks = (page = 1, size = 10) => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchBooks = async () => {
      try {
        setLoading(true);
        const data = await booksAPI.getBooks(page, size);
        setBooks(data.books);
        setTotal(data.total);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching books:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchBooks();
  }, [page, size]);

  return { books, loading, error, total };
};
```

### 5. Example React Component
```javascript
// src/components/BooksList.js
import React from 'react';
import { useBooks } from '../hooks/useBooks';

const BooksList = () => {
  const { books, loading, error, total } = useBooks(1, 10);

  if (loading) return <div>Loading books...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Pure Bhakti Books ({total} total)</h1>
      <div className="books-grid">
        {books.map(book => (
          <div key={book.book_id} className="book-card">
            <h3>{book.original_book_title}</h3>
            <p><strong>English:</strong> {book.english_book_title}</p>
            <p><strong>Author:</strong> {book.original_author}</p>
            <p><strong>Pages:</strong> {book.number_of_pages}</p>
            <p><strong>Edition:</strong> {book.edition}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BooksList;
```

## CORS Configuration (if needed)

If you encounter CORS issues, update your FastAPI `main.py`:

```python
# In app/main.py, update CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

## Docker Compose for Full Stack

Create `docker-compose.fullstack.yml`:

```yaml
services:
  # Your existing API services
  api:
    build: ./purebhakti_apis
    environment:
      - DATABASE_URL=postgresql://pbbdbuser:Govinda2025%23@host.docker.internal:5432/pure_bhakti_vault
      # ... other env vars
    expose:
      - "8000"

  nginx:
    image: nginx:alpine
    ports:
      - "8080:80"
      - "8443:443"
    volumes:
      - ./purebhakti_apis/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./purebhakti_apis/ssl:/etc/ssl:ro
    depends_on:
      - api

  # React frontend
  frontend:
    build: ./your-react-app
    ports:
      - "3000:80"  # Serve React on port 3000
    environment:
      - REACT_APP_API_URL=https://localhost:8443
    depends_on:
      - nginx
```

## Development Workflow

```bash
# Terminal 1: Start API services
cd purebhakti_apis
docker-compose up -d

# Terminal 2: Start React development
cd your-react-app
npm start

# Access points:
# React App: http://localhost:3000
# API: https://localhost:8443
```

## Production Deployment

For production, both React and API can be served by the same nginx:

```nginx
# In production nginx config
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # Serve React app
    location / {
        root /var/www/react-build;
        try_files $uri $uri/ /index.html;
    }

    # API routes
    location /api/ {
        proxy_pass http://api:8000;
        # ... proxy headers
    }

    # API docs
    location /docs {
        proxy_pass http://api:8000/docs;
    }
}
```

This setup gives you:
- ✅ **Separate development** (React:3000, API:8443)
- ✅ **No port conflicts**
- ✅ **SSL security** for API calls
- ✅ **Easy production deployment**