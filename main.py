"""
Main FastAPI Application
Payment Document Chatbot API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path

from config import settings
from api.chat_endpoints import router as chat_router
from api.document_upload import router as docs_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Multi-stakeholder Payment Document Chatbot with RAG"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for serving JS files
frontend_dir = Path("frontend")
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    logger.info("Frontend static files mounted at /static")

# Include routers
app.include_router(chat_router, prefix=settings.API_PREFIX)
app.include_router(docs_router, prefix=settings.API_PREFIX)


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend interface"""
    frontend_path = Path("frontend/chat_interface.html")
    
    if frontend_path.exists():
        with open(frontend_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    else:
        # Fallback to API info if frontend not available
        logger.warning("Frontend not found. Please create frontend/chat_interface.html")
        return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Payment Chatbot API</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            max-width: 800px;
                            margin: 50px auto;
                            padding: 20px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                        }
                        .container {
                            background: white;
                            color: #333;
                            padding: 40px;
                            border-radius: 12px;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        }
                        h1 { color: #667eea; }
                        a {
                            color: #667eea;
                            text-decoration: none;
                            font-weight: bold;
                        }
                        a:hover { text-decoration: underline; }
                        .setup-steps {
                            background: #f8f9fa;
                            padding: 20px;
                            border-radius: 8px;
                            margin-top: 20px;
                        }
                        .setup-steps li {
                            margin: 10px 0;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>💳 Payment Document Chatbot API</h1>
                        <p><strong>Version:</strong> """ + settings.API_VERSION + """</p>
                        
                        <div class="setup-steps">
                            <h3>⚠️ Frontend Setup Required</h3>
                            <p>The frontend files are missing. Follow these steps:</p>
                            <ol>
                                <li>Create the <code>frontend/</code> directory</li>
                                <li>Add <code>chat_interface.html</code></li>
                                <li>Add <code>role_selector.js</code></li>
                                <li>Add <code>document_viewer.js</code></li>
                                <li>Restart the server</li>
                            </ol>
                        </div>
                        
                        <h3>📚 API Documentation</h3>
                        <p><a href="/docs">Interactive API Documentation (Swagger UI)</a></p>
                        <p><a href="/redoc">Alternative Documentation (ReDoc)</a></p>
                        
                        <h3>🔍 Health Check</h3>
                        <p><a href="/health">Check API Health Status</a></p>
                    </div>
                </body>
            </html>
        """)


@app.get("/health")
async def health_check():
    """Global health check"""
    frontend_exists = Path("frontend/chat_interface.html").exists()
    js_files_exist = (
        Path("frontend/role_selector.js").exists() and 
        Path("frontend/document_viewer.js").exists()
    )
    
    return {
        "status": "healthy",
        "service": "payment-chatbot",
        "version": settings.API_VERSION,
        "frontend": {
            "html": frontend_exists,
            "javascript": js_files_exist,
            "ready": frontend_exists and js_files_exist
        }
    }


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info("API will be available at http://localhost:8000")
    logger.info("API docs available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)