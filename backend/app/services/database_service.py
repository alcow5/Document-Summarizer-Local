"""
Database Service for Privacy-Focused AI Document Summarizer
Handles all SQLite database operations with encryption support
"""

import sqlite3
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from loguru import logger

from ..config import get_database_path


class DatabaseService:
    """Service for managing SQLite database operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_config = config["database"]
        self.db_path = get_database_path(config)
        self.encryption_key = self.db_config.get("encryption_key")
        self.max_summaries = self.db_config.get("max_summaries", 50)
        
        self.connection = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize database connection and create tables if needed"""
        try:
            # Create database directory if it doesn't exist
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Enable WAL mode for better concurrent access
            self.connection.execute("PRAGMA journal_mode=WAL")
            
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys=ON")
            
            # Set encryption key if available (requires SQLCipher)
            if self.encryption_key:
                try:
                    self.connection.execute(f"PRAGMA key = '{self.encryption_key}'")
                    logger.info("Database encryption enabled")
                except sqlite3.OperationalError:
                    logger.warning("SQLCipher not available, database will not be encrypted")
            
            # Create tables if they don't exist
            await self._create_tables()
            
            # Verify database works
            await self._verify_database()
            
            self.is_initialized = True
            logger.info(f"Database service initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            if self.connection:
                self.connection.close()
            raise
    
    async def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            # Read schema from file
            schema_path = self.db_path.parent.parent / "database" / "schema.sql"
            
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                
                # Execute schema in chunks (SQLite doesn't handle multiple statements well)
                statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
                
                for statement in statements:
                    try:
                        self.connection.execute(statement)
                    except sqlite3.Error as e:
                        if "already exists" not in str(e).lower():
                            logger.warning(f"Schema statement failed: {e}")
                
                self.connection.commit()
                logger.info("Database schema created/updated")
            else:
                logger.warning(f"Schema file not found: {schema_path}")
                # Create basic tables as fallback
                await self._create_basic_tables()
                
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    async def _create_basic_tables(self):
        """Create basic tables as fallback if schema file not found"""
        basic_schema = """
        CREATE TABLE IF NOT EXISTS summaries (
            doc_id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            file_extension TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            summary TEXT NOT NULL,
            insights TEXT,
            template TEXT NOT NULL,
            processing_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS app_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT NOT NULL,
            setting_type TEXT DEFAULT 'string',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        self.connection.executescript(basic_schema)
        self.connection.commit()
        logger.info("Basic database schema created")
    
    async def _verify_database(self):
        """Verify database is working correctly"""
        try:
            # Test basic operations
            cursor = self.connection.execute("SELECT COUNT(*) FROM summaries")
            count = cursor.fetchone()[0]
            logger.info(f"Database verification passed. Current summaries: {count}")
            
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            raise
    
    async def save_summary(
        self,
        filename: str,
        summary: str,
        insights: List[str],
        template: str,
        file_size: int,
        processing_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Save a document summary to the database"""
        try:
            doc_id = str(uuid.uuid4())
            file_extension = Path(filename).suffix.lower().lstrip('.')
            insights_json = json.dumps(insights) if insights else None
            timestamp = datetime.utcnow()
            
            # Insert summary
            self.connection.execute("""
                INSERT INTO summaries (
                    doc_id, filename, file_extension, file_size,
                    summary, insights, template, processing_time, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id, filename, file_extension, file_size,
                summary, insights_json, template, processing_time, timestamp
            ))
            
            self.connection.commit()
            
            # Cleanup old summaries if needed
            await self._cleanup_old_summaries()
            
            logger.info(f"Summary saved: {doc_id}")
            
            return {
                "doc_id": doc_id,
                "filename": filename,
                "summary": summary,
                "insights": insights,
                "template": template,
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")
            raise
    
    async def get_summaries(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get summaries with pagination"""
        try:
            cursor = self.connection.execute("""
                SELECT doc_id, filename, summary, template, created_at, processing_time
                FROM summaries
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            summaries = []
            for row in cursor.fetchall():
                summaries.append({
                    "doc_id": row["doc_id"],
                    "filename": row["filename"],
                    "summary": row["summary"],
                    "template": row["template"],
                    "timestamp": row["created_at"],
                    "processing_time": row["processing_time"]
                })
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to get summaries: {e}")
            return []
    
    async def get_summary_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific summary by ID"""
        try:
            cursor = self.connection.execute("""
                SELECT * FROM summaries WHERE doc_id = ?
            """, (doc_id,))
            
            row = cursor.fetchone()
            if row:
                insights = json.loads(row["insights"]) if row["insights"] else []
                return {
                    "doc_id": row["doc_id"],
                    "filename": row["filename"],
                    "summary": row["summary"],
                    "insights": insights,
                    "template": row["template"],
                    "processing_time": row["processing_time"],
                    "timestamp": row["created_at"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get summary {doc_id}: {e}")
            return None
    
    async def delete_summary(self, doc_id: str) -> bool:
        """Delete a summary by ID"""
        try:
            cursor = self.connection.execute("""
                DELETE FROM summaries WHERE doc_id = ?
            """, (doc_id,))
            
            deleted = cursor.rowcount > 0
            self.connection.commit()
            
            if deleted:
                logger.info(f"Summary deleted: {doc_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete summary {doc_id}: {e}")
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get application statistics"""
        try:
            # Total summaries
            cursor = self.connection.execute("SELECT COUNT(*) FROM summaries")
            total_summaries = cursor.fetchone()[0]
            
            # Summaries this week
            week_ago = datetime.utcnow() - timedelta(days=7)
            cursor = self.connection.execute("""
                SELECT COUNT(*) FROM summaries 
                WHERE created_at >= ?
            """, (week_ago,))
            summaries_this_week = cursor.fetchone()[0]
            
            # Most used template
            cursor = self.connection.execute("""
                SELECT template, COUNT(*) as count 
                FROM summaries 
                GROUP BY template 
                ORDER BY count DESC 
                LIMIT 1
            """)
            template_row = cursor.fetchone()
            most_used_template = template_row[0] if template_row else "None"
            
            # Average processing time
            cursor = self.connection.execute("""
                SELECT AVG(processing_time) FROM summaries 
                WHERE processing_time IS NOT NULL
            """)
            avg_time_row = cursor.fetchone()
            avg_processing_time = avg_time_row[0] if avg_time_row and avg_time_row[0] else 0.0
            
            # Total documents processed (same as total summaries for now)
            total_documents_processed = total_summaries
            
            return {
                "total_summaries": total_summaries,
                "summaries_this_week": summaries_this_week,
                "most_used_template": most_used_template,
                "avg_processing_time": round(avg_processing_time, 2),
                "total_documents_processed": total_documents_processed
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                "total_summaries": 0,
                "summaries_this_week": 0,
                "most_used_template": "None",
                "avg_processing_time": 0.0,
                "total_documents_processed": 0
            }
    
    async def cleanup_old_summaries(self):
        """Clean up old summaries based on max_summaries setting"""
        try:
            # Check if we exceed the limit
            cursor = self.connection.execute("SELECT COUNT(*) FROM summaries")
            count = cursor.fetchone()[0]
            
            if count > self.max_summaries:
                # Delete oldest summaries
                excess = count - self.max_summaries
                self.connection.execute("""
                    DELETE FROM summaries 
                    WHERE doc_id IN (
                        SELECT doc_id FROM summaries 
                        ORDER BY created_at ASC 
                        LIMIT ?
                    )
                """, (excess,))
                
                self.connection.commit()
                logger.info(f"Cleaned up {excess} old summaries")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old summaries: {e}")
    
    async def _cleanup_old_summaries(self):
        """Internal cleanup method"""
        await self.cleanup_old_summaries()
    
    async def health_check(self) -> str:
        """Check database health"""
        try:
            if not self.is_initialized:
                return "not_initialized"
            
            # Test basic operations
            cursor = self.connection.execute("SELECT 1")
            cursor.fetchone()
            
            # Check integrity
            cursor = self.connection.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            if result == "ok":
                return "healthy"
            else:
                return f"integrity_failed"
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return "unhealthy"
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    # Additional utility methods
    
    async def export_summaries(self, format_type: str = "json") -> str:
        """Export all summaries to specified format"""
        try:
            summaries = await self.get_summaries(limit=1000)  # Get all
            
            if format_type == "json":
                return json.dumps(summaries, indent=2, default=str)
            elif format_type == "csv":
                # Simple CSV export
                if not summaries:
                    return ""
                
                headers = summaries[0].keys()
                csv_lines = [",".join(headers)]
                
                for summary in summaries:
                    row = []
                    for key in headers:
                        value = str(summary[key]).replace('"', '""')
                        row.append(f'"{value}"')
                    csv_lines.append(",".join(row))
                
                return "\n".join(csv_lines)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            logger.error(f"Failed to export summaries: {e}")
            raise
    
    async def get_summary_count(self) -> int:
        """Get total number of summaries"""
        try:
            cursor = self.connection.execute("SELECT COUNT(*) FROM summaries")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to get summary count: {e}")
            return 0 