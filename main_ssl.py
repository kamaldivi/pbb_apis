import uvicorn
from app.main import app

if __name__ == "__main__":
    # SSL-enabled FastAPI server for direct HTTPS access
    # This bypasses nginx and serves HTTPS directly from FastAPI
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8443,
        ssl_keyfile="ssl/purebhaktibase.com.key",
        ssl_certfile="ssl/purebhaktibase.com.crt",
        reload=True
    )