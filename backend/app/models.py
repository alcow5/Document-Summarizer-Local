"""
Pydantic models for Privacy-Focused AI Document Summarizer
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentFormat(str, Enum):
    """Supported document formats"""
    PDF = "pdf"
    DOCX = "docx"


class SummaryTemplate(str, Enum):
    """Available summary templates"""
    GENERAL = "general"
    CUSTOMER_FEEDBACK = "customer_feedback"
    CONTRACT_ANALYSIS = "contract_analysis"


class SummaryRequest(BaseModel):
    """Request model for document summarization"""
    template: SummaryTemplate = SummaryTemplate.GENERAL
    custom_prompt: Optional[str] = Field(None, max_length=1000, description="Custom prompt for summarization")
    
    @validator('custom_prompt')
    def validate_custom_prompt(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v


class SummaryResponse(BaseModel):
    """Response model for document summarization"""
    doc_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    summary: str = Field(..., description="Generated summary")
    insights: List[str] = Field(default_factory=list, description="Key insights extracted")
    processing_time: float = Field(..., description="Processing time in seconds")
    template: str = Field(..., description="Template used for summarization")
    timestamp: datetime = Field(..., description="When the summary was created")
    token_count: Optional[int] = Field(None, description="Number of tokens processed")
    model_used: Optional[str] = Field(None, description="LLM model used")


class HistoryResponse(BaseModel):
    """Response model for summary history"""
    doc_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    summary: str = Field(..., description="Summary preview (truncated)")
    template: str = Field(..., description="Template used")
    timestamp: datetime = Field(..., description="Creation timestamp")


class ModelInfo(BaseModel):
    """Model information response"""
    name: str = Field(..., description="Model name")
    version: str = Field(..., description="Model version")
    size: Optional[str] = Field(None, description="Model size")
    quantization: Optional[str] = Field(None, description="Quantization type")
    context_window: int = Field(..., description="Context window size")
    status: str = Field(..., description="Model status")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")


class TemplateInfo(BaseModel):
    """Template information"""
    name: str = Field(..., description="Template display name")
    key: str = Field(..., description="Template key identifier")
    description: str = Field(..., description="Template description")
    prompt: str = Field(..., description="Template prompt")
    use_cases: List[str] = Field(default_factory=list, description="Common use cases")


class DocumentMetadata(BaseModel):
    """Document metadata"""
    filename: str = Field(..., description="Document filename")
    file_size: int = Field(..., description="File size in bytes")
    file_extension: DocumentFormat = Field(..., description="File format")
    page_count: Optional[int] = Field(None, description="Number of pages")
    word_count: Optional[int] = Field(None, description="Word count")
    language: Optional[str] = Field(None, description="Detected language")
    
    @validator('file_size')
    def validate_file_size(cls, v):
        if v <= 0:
            raise ValueError('File size must be positive')
        return v


class ProcessingStats(BaseModel):
    """Processing statistics"""
    total_summaries: int = Field(..., description="Total number of summaries")
    summaries_this_week: int = Field(..., description="Summaries created this week")
    summaries_this_month: int = Field(..., description="Summaries created this month")
    avg_processing_time: float = Field(..., description="Average processing time")
    most_used_template: str = Field(..., description="Most frequently used template")
    total_documents_processed: int = Field(..., description="Total documents processed")
    total_bytes_processed: int = Field(..., description="Total bytes processed")


class UserPreference(BaseModel):
    """User preference model"""
    key: str = Field(..., description="Preference key")
    value: Any = Field(..., description="Preference value")
    data_type: str = Field(..., description="Data type")
    
    @validator('key')
    def validate_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Preference key cannot be empty')
        return v.strip()


class AppSettings(BaseModel):
    """Application settings model"""
    max_summaries: int = Field(50, description="Maximum summaries to keep")
    auto_cleanup: bool = Field(True, description="Auto cleanup old summaries")
    encryption_enabled: bool = Field(True, description="Database encryption enabled")
    model_auto_update: bool = Field(True, description="Auto check for model updates")
    
    @validator('max_summaries')
    def validate_max_summaries(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Max summaries must be between 1 and 1000')
        return v


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Overall health status")
    services: Dict[str, str] = Field(..., description="Individual service statuses")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")


class ModelUpdateRequest(BaseModel):
    """Model update request"""
    check_only: bool = Field(False, description="Only check for updates, don't download")
    force_update: bool = Field(False, description="Force update even if current")


class ModelUpdateResponse(BaseModel):
    """Model update response"""
    update_available: bool = Field(..., description="Whether an update is available")
    current_version: str = Field(..., description="Current model version")
    latest_version: Optional[str] = Field(None, description="Latest available version")
    download_size: Optional[int] = Field(None, description="Download size in bytes")
    changelog: Optional[str] = Field(None, description="Update changelog")
    update_started: bool = Field(False, description="Whether update was started")


class InsightData(BaseModel):
    """Insight data model"""
    type: str = Field(..., description="Type of insight")
    label: str = Field(..., description="Insight label")
    value: Any = Field(..., description="Insight value")
    confidence: Optional[float] = Field(None, description="Confidence score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ChartData(BaseModel):
    """Chart data for visualization"""
    type: str = Field(..., description="Chart type (bar, pie, line, etc.)")
    title: str = Field(..., description="Chart title")
    labels: List[str] = Field(..., description="Chart labels")
    datasets: List[Dict[str, Any]] = Field(..., description="Chart datasets")
    options: Optional[Dict[str, Any]] = Field(None, description="Chart options")


class ExportRequest(BaseModel):
    """Export request model"""
    doc_ids: Optional[List[str]] = Field(None, description="Specific document IDs to export")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    templates: Optional[List[str]] = Field(None, description="Template filter")
    format: str = Field("json", description="Export format")
    
    @validator('format')
    def validate_format(cls, v):
        if v not in ["json", "csv", "txt"]:
            raise ValueError('Format must be json, csv, or txt')
        return v


class BackupRequest(BaseModel):
    """Database backup request"""
    include_summaries: bool = Field(True, description="Include summary data")
    include_settings: bool = Field(True, description="Include settings")
    include_stats: bool = Field(False, description="Include statistics")
    encrypt_backup: bool = Field(True, description="Encrypt backup file")


class RestoreRequest(BaseModel):
    """Database restore request"""
    backup_file_path: str = Field(..., description="Path to backup file")
    restore_summaries: bool = Field(True, description="Restore summary data")
    restore_settings: bool = Field(True, description="Restore settings")
    merge_data: bool = Field(False, description="Merge with existing data")
    
    @validator('backup_file_path')
    def validate_backup_path(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Backup file path cannot be empty')
        return v.strip()


# Response wrapper for consistent API responses
class ApiResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[ErrorResponse] = Field(None, description="Error information")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp") 