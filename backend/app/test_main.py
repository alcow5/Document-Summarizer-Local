"""
Test version of main.py that can run without Ollama for basic API testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from config import load_config

# Load configuration
config = load_config()

# Simple FastAPI app for testing
app = FastAPI(
    title=config["app"]["name"] + " (Test Mode)",
    description="Test API without LLM dependencies",
    version=config["app"]["version"],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config["security"]["cors_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Privacy-Focused AI Document Summarizer API (Test Mode)",
        "version": config["app"]["version"],
        "status": "running",
        "mode": "test"
    }

@app.get("/health")
async def health_check():
    """Simple health check without external dependencies"""
    return {
        "status": "healthy",
        "services": {
            "database": "not_tested",
            "llm": "disabled",
            "document_processor": "available"
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/templates")
async def get_templates():
    """Get available summary templates"""
    templates = config["templates"]
    return {
        name: {
            "name": template["name"],
            "description": template.get("description", "")
        }
        for name, template in templates.items()
    }

@app.get("/test/config")
async def test_config():
    """Test endpoint to verify configuration loading"""
    return {
        "app_name": config["app"]["name"],
        "version": config["app"]["version"],
        "supported_formats": config["documents"]["supported_formats"],
        "templates_available": list(config["templates"].keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config["app"]["host"],
        port=config["app"]["port"],
        reload=False,
        log_level="info"
    ) 