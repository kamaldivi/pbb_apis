# Pure Bhakti Glossary Search API

## Overview

The Glossary Search API provides intelligent semantic search across 4,182 spiritual terms from 29 sacred books, with built-in content filtering to protect the sanctity of the material.

## Features

✅ **Semantic Search** - AI-powered understanding of meaning, not just keywords
✅ **Multi-book Search** - Searches across all 29 books simultaneously
✅ **Content Filtering** - Blocks inappropriate queries automatically
✅ **Automatic Fallback** - Falls back to text search if AI service is unavailable
✅ **No Authentication Required** - Public endpoint (protected by content filter)

## API Endpoint

### POST `/api/v1/glossary/search`

**Request Body:**
```json
{
  "query": "water purification ritual",
  "limit": 5,
  "book_id": null
}
```

**Parameters:**
- `query` (string, required): Search query text (2-200 characters)
- `limit` (integer, optional): Number of results (1-20, default: 5)
- `book_id` (integer, optional): Filter by specific book (null = search all books)

**Response:**
```json
{
  "results": [
    {
      "term": "ācamana",
      "description": "a ritual of purification in which one sips water...",
      "book_name": "Arcana-dipika - 3rd Edition",
      "book_id": 2
    }
  ],
  "total_found": 1,
  "query": "water purification ritual",
  "message": null
}
```

## Example Queries

### Good Queries ✅
```bash
# Semantic search - finds conceptually related terms
curl -X POST http://localhost:8000/api/v1/glossary/search \
  -H "Content-Type: application/json" \
  -d '{"query": "spiritual teacher", "limit": 5}'
# Returns: guru, śikṣā-guru, ācārya

curl -X POST http://localhost:8000/api/v1/glossary/search \
  -H "Content-Type: application/json" \
  -d '{"query": "devotional singing", "limit": 5}'
# Returns: kīrtana, bhajana, saṅkīrtana

# Filter by specific book
curl -X POST http://localhost:8000/api/v1/glossary/search \
  -H "Content-Type: application/json" \
  -d '{"query": "love", "limit": 10, "book_id": 41}'
```

### Blocked Queries ❌
```bash
# Inappropriate content - automatically rejected
curl -X POST http://localhost:8000/api/v1/glossary/search \
  -H "Content-Type: application/json" \
  -d '{"query": "bad word here", "limit": 5}'
# Returns: 400 Bad Request
# "Your search query cannot be processed. Please use respectful language..."
```

## How It Works

### 1. Content Filter (First Line of Defense)
- Sanitizes input
- Checks against blocked words list
- Detects spam patterns
- Validates query length and format

### 2. Semantic Search (Primary Method)
- Converts query to 1024-dimensional embedding using Ollama (bge-m3 model)
- Compares against 4,182 pre-stored glossary embeddings in PostgreSQL
- Uses pgvector cosine similarity for fast matching
- Returns top N most semantically similar terms

### 3. Text Fallback (Backup Method)
- If Ollama is unavailable, automatically uses traditional text search
- Searches term and description fields using PostgreSQL ILIKE
- Ensures users always get results

## Prerequisites

### Required Services

1. **PostgreSQL with pgvector** ✅ Already configured
   - glossary_embeddings table populated with 4,182 entries
   - IVFFlat index for fast similarity search

2. **Ollama** (for semantic search)
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.com/install.sh | sh

   # Pull bge-m3 model
   ollama pull bge-m3

   # Start Ollama service
   ollama serve
   ```

   **Note:** If Ollama is not running, the API will automatically fall back to text search

## Content Protection

### Blocked Words Management

Edit the blocked words list at:
```
app/config/blocked_words.txt
```

**Format:**
```text
# Comments start with #
# One word per line (case-insensitive)

badword1
badword2
inappropriate_term
```

**Auto-reload:** Changes take effect on next API restart

### What Gets Blocked

1. **Profanity** - Common curse words and variations
2. **Sexual Content** - Explicit or suggestive terms
3. **Violence** - Violent or aggressive language
4. **Hate Speech** - Discriminatory or hateful terms
5. **Spam** - Repeated characters, excessive special characters
6. **Invalid Input** - Too short, too long, or empty queries

### Protection Layers

```
User Query
    ↓
[1. Query Sanitization]
    ↓
[2. Blocked Words Check]
    ↓
[3. Pattern Matching (variations)]
    ↓
[4. Spam Detection]
    ↓
[5. Length Validation]
    ↓
Semantic Search (on pure glossary database)
```

## Database Statistics

```
Total glossary embeddings: 4,182
Books with embeddings: 29
Vector dimensions: 1024
Index type: IVFFlat (cosine distance)
```

## Performance

- **Semantic Search:** ~100-300ms (with Ollama)
- **Text Search:** ~50-100ms (without Ollama)
- **Content Filter:** ~1-2ms

## Monitoring

### Check if Ollama is Running
```bash
curl http://localhost:11434/api/tags
```

### Check Glossary Embeddings Stats
```bash
curl http://localhost:8000/api/v1/glossary/embeddings/stats
```

### View Server Logs
```bash
# Watch for rejected queries
tail -f logs/api.log | grep "Inappropriate query rejected"
```

## Security Notes

1. **No Authentication**: Endpoint is public but protected by content filter
2. **Rate Limiting**: Consider adding rate limiting in production
3. **Logging**: All rejected queries are logged with timestamps
4. **Database**: Glossary content is read-only for search operations

## Troubleshooting

### Semantic Search Not Working
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama
ollama serve

# Verify bge-m3 model is available
ollama list | grep bge-m3
```

### No Results Returned
- API automatically tries text search as fallback
- Check if the glossary database has embeddings:
  ```bash
  curl http://localhost:8000/api/v1/glossary/embeddings/stats
  ```

### False Positive Blocks
- Edit `app/config/blocked_words.txt`
- Remove overly broad terms
- Restart API server

## Future Enhancements

Potential improvements:
- [ ] Rate limiting per IP
- [ ] Query logging and analytics
- [ ] Multi-language support
- [ ] Advanced filtering (by date, author, etc.)
- [ ] Search suggestions/autocomplete
- [ ] User feedback on search quality

## Support

For issues or questions:
- Check server logs: `logs/api.log`
- Verify Ollama status: `ollama list`
- Test database connection: Check `/health` endpoint
