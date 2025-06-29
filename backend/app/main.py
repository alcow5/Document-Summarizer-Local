"""
Privacy-Focused AI Document Summarizer - Main FastAPI Application
"""

import os
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import yaml
from loguru import logger

from .models import SummaryRequest, SummaryResponse, HistoryResponse, ModelInfo
from .services.document_processor import DocumentProcessor
from .services.llm_service import LLMService
from .services.database_service import DatabaseService
from .services.model_updater import ModelUpdater
from .config import load_config
from .middleware import SecurityMiddleware, RateLimitMiddleware

# Load configuration
config = load_config()

# Global service instances
document_processor = None
llm_service = None
database_service = None
model_updater = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    global document_processor, llm_service, database_service, model_updater
    
    # Startup
    logger.info("Starting Privacy-Focused AI Document Summarizer...")
    
    # Initialize services
    database_service = DatabaseService(config)
    await database_service.initialize()
    
    llm_service = LLMService(config)
    await llm_service.initialize()
    
    document_processor = DocumentProcessor(config)
    model_updater = ModelUpdater(config)
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    if database_service:
        await database_service.close()
    logger.info("Application shutdown complete")


# FastAPI app instance
app = FastAPI(
    title=config["app"]["name"],
    description=config["app"]["description"],
    version=config["app"]["version"],
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config["security"]["cors_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware, config=config)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Privacy-Focused AI Document Summarizer API",
        "version": config["app"]["version"],
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check LLM service
        llm_status = await llm_service.health_check()
        
        # Check database
        db_status = await database_service.health_check()
        
        return {
            "status": "healthy",
            "services": {
                "llm": llm_status,
                "database": db_status,
                "document_processor": "healthy"
            },
            "timestamp": str(datetime.utcnow())
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/summarize", response_model=SummaryResponse)
async def summarize_document(
    file: UploadFile = File(...),
    template: str = "general",
    custom_prompt: Optional[str] = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Summarize an uploaded document using the specified template or custom prompt
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in config["documents"]["supported_formats"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format. Supported: {config['documents']['supported_formats']}"
            )
        
        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        max_size = config["documents"]["max_file_size_mb"] * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {config['documents']['max_file_size_mb']}MB"
            )
        
        # Process document
        logger.info(f"Processing document: {file.filename}")
        text_chunks = await document_processor.extract_text(content, file_extension)
        
        # Generate summary using LLM
        prompt_template = custom_prompt or config["templates"][template]["prompt"]
        summary_result = await llm_service.summarize(text_chunks, prompt_template)
        
        # Save to database
        doc_record = await database_service.save_summary(
            filename=file.filename,
            summary=summary_result["summary"],
            insights=summary_result["insights"],
            template=template,
            file_size=file_size
        )
        
        # Schedule cleanup task
        background_tasks.add_task(database_service.cleanup_old_summaries)
        
        return SummaryResponse(
            doc_id=doc_record["doc_id"],
            filename=file.filename,
            summary=summary_result["summary"],
            insights=summary_result["insights"],
            processing_time=summary_result["processing_time"],
            template=template,
            timestamp=doc_record["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/history", response_model=List[HistoryResponse])
async def get_summary_history(
    limit: int = 50,
    offset: int = 0
):
    """Get summary history from local database"""
    try:
        summaries = await database_service.get_summaries(limit=limit, offset=offset)
        return [
            HistoryResponse(
                doc_id=s["doc_id"],
                filename=s["filename"],
                summary=s["summary"][:200] + "..." if len(s["summary"]) > 200 else s["summary"],
                template=s["template"],
                timestamp=s["timestamp"]
            )
            for s in summaries
        ]
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving history")


@app.get("/summary/{doc_id}", response_model=SummaryResponse)
async def get_summary(doc_id: str):
    """Get a specific summary by ID"""
    try:
        summary = await database_service.get_summary_by_id(doc_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        return SummaryResponse(**summary)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving summary {doc_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving summary")


@app.delete("/summary/{doc_id}")
async def delete_summary(doc_id: str):
    """Delete a summary from the database"""
    try:
        deleted = await database_service.delete_summary(doc_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Summary not found")
        
        return {"message": "Summary deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting summary {doc_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting summary")


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


@app.get("/model/info", response_model=ModelInfo)
async def get_model_info():
    """Get information about the current LLM model"""
    try:
        model_info = await llm_service.get_model_info()
        return ModelInfo(**model_info)
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving model information")


@app.post("/model/update")
async def update_model(background_tasks: BackgroundTasks):
    """Check for and download model updates"""
    try:
        # Schedule update check in background
        background_tasks.add_task(model_updater.check_and_update)
        return {"message": "Model update check started"}
    except Exception as e:
        logger.error(f"Error starting model update: {e}")
        raise HTTPException(status_code=500, detail="Error starting model update")


@app.get("/stats")
async def get_statistics():
    """Get application statistics"""
    try:
        stats = await database_service.get_statistics()
        return {
            "total_summaries": stats["total_summaries"],
            "summaries_this_week": stats["summaries_this_week"],
            "most_used_template": stats["most_used_template"],
            "avg_processing_time": stats["avg_processing_time"],
            "total_documents_processed": stats["total_documents_processed"]
        }
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")


# Error handlers
@app.exception_handler(413)
async def file_too_large_handler(request, exc):
    return JSONResponse(
        status_code=413,
        content={"detail": "File too large"}
    )


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=config["app"]["host"],
        port=config["app"]["port"],
        reload=config["app"]["debug"],
        log_level="info"
    ) 