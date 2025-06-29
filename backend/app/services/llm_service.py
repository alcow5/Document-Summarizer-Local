"""
LLM Service for communicating with Ollama and TinyLlama
Handles document summarization and AI model operations
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any, Optional
from loguru import logger


class LLMService:
    """Service for interacting with local LLM via Ollama"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_config = config["model"]
        self.host = self.model_config["host"]
        self.model_name = self.model_config["name"]
        self.context_window = self.model_config.get("context_window", 4096)
        self.temperature = self.model_config.get("temperature", 0.7)
        self.max_tokens = self.model_config.get("max_tokens", 4096)
        
        self.session = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the LLM service and check model availability"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
            )
            
            # Check if Ollama is running
            await self._check_ollama_health()
            
            # Check if our model is available
            await self._ensure_model_available()
            
            self.is_initialized = True
            logger.info(f"LLM service initialized with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            if self.session:
                await self.session.close()
            raise
    
    async def _check_ollama_health(self):
        """Check if Ollama server is responding"""
        try:
            async with self.session.get(f"{self.host}/api/tags") as response:
                if response.status == 200:
                    logger.info("Ollama server is responding")
                    return True
                else:
                    raise Exception(f"Ollama server returned status {response.status}")
        except Exception as e:
            logger.error(f"Ollama server health check failed: {e}")
            raise Exception(f"Cannot connect to Ollama at {self.host}. Please ensure Ollama is running.")
    
    async def _ensure_model_available(self):
        """Check if the required model is available"""
        try:
            async with self.session.get(f"{self.host}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    
                    if self.model_name in models or f"{self.model_name}:latest" in models:
                        logger.info(f"Model {self.model_name} is available")
                        return True
                    else:
                        logger.warning(f"Model {self.model_name} not found. Available models: {models}")
                        logger.info(f"Attempting to pull model {self.model_name}...")
                        await self._pull_model()
                        return True
                else:
                    raise Exception(f"Failed to list models: {response.status}")
        except Exception as e:
            logger.error(f"Model availability check failed: {e}")
            raise
    
    async def _pull_model(self):
        """Pull the required model from Ollama"""
        try:
            pull_data = {"name": self.model_name}
            
            async with self.session.post(
                f"{self.host}/api/pull",
                json=pull_data
            ) as response:
                if response.status == 200:
                    # Stream the response to show progress
                    async for line in response.content:
                        if line:
                            try:
                                status = json.loads(line.decode())
                                if "status" in status:
                                    logger.info(f"Pull status: {status['status']}")
                            except json.JSONDecodeError:
                                continue
                    
                    logger.info(f"Successfully pulled model {self.model_name}")
                else:
                    raise Exception(f"Failed to pull model: {response.status}")
        except Exception as e:
            logger.error(f"Model pull failed: {e}")
            raise
    
    async def summarize(self, text_chunks: List[str], prompt_template: str) -> Dict[str, Any]:
        """
        Summarize document chunks using the LLM
        
        Args:
            text_chunks: List of text chunks from document
            prompt_template: Template for the summarization prompt
            
        Returns:
            Dictionary with summary, insights, and processing time
        """
        if not self.is_initialized:
            raise Exception("LLM service not initialized")
        
        start_time = time.time()
        
        try:
            # Process chunks individually if multiple
            if len(text_chunks) == 1:
                summary = await self._generate_summary(text_chunks[0], prompt_template)
            else:
                # For multiple chunks, summarize each and then create final summary
                chunk_summaries = []
                for i, chunk in enumerate(text_chunks):
                    logger.info(f"Processing chunk {i+1}/{len(text_chunks)}")
                    chunk_summary = await self._generate_summary(chunk, prompt_template)
                    chunk_summaries.append(chunk_summary)
                
                # Combine chunk summaries into final summary
                combined_text = "\n\n".join(chunk_summaries)
                final_prompt = f"Create a comprehensive summary from these partial summaries:\n\n{combined_text}"
                summary = await self._generate_summary(combined_text, final_prompt, max_length=300)
            
            # Extract insights from summary
            insights = await self._extract_insights(summary)
            
            processing_time = time.time() - start_time
            
            result = {
                "summary": summary,
                "insights": insights,
                "processing_time": processing_time,
                "chunks_processed": len(text_chunks)
            }
            
            logger.info(f"Summarization completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise
    
    async def _generate_summary(self, text: str, prompt_template: str, max_length: int = 200) -> str:
        """Generate summary for a single text chunk"""
        try:
            # Format the prompt
            full_prompt = prompt_template.format(text=text)
            
            # Prepare request data
            request_data = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": max_length * 2,  # Rough token estimate
                    "stop": ["\n\n\n", "END_SUMMARY"]
                }
            }
            
            # Make request to Ollama
            async with self.session.post(
                f"{self.host}/api/generate",
                json=request_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    summary = data.get("response", "").strip()
                    
                    if not summary:
                        raise Exception("Empty response from LLM")
                    
                    return summary
                else:
                    error_text = await response.text()
                    raise Exception(f"LLM request failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            raise
    
    async def _extract_insights(self, summary: str) -> List[str]:
        """Extract key insights from the summary"""
        try:
            insight_prompt = f"""
Extract 3-5 key insights from this summary as bullet points:

{summary}

Format as simple bullet points, one insight per line:
"""
            
            request_data = {
                "model": self.model_name,
                "prompt": insight_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more focused insights
                    "num_predict": 200
                }
            }
            
            async with self.session.post(
                f"{self.host}/api/generate",
                json=request_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    insights_text = data.get("response", "").strip()
                    
                    # Parse insights into list
                    insights = []
                    for line in insights_text.split('\n'):
                        line = line.strip()
                        if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                            insight = line.lstrip('•-* ').strip()
                            if insight:
                                insights.append(insight)
                    
                    # Fallback if no bullet points found
                    if not insights and insights_text:
                        insights = [insights_text[:100] + "..." if len(insights_text) > 100 else insights_text]
                    
                    return insights[:5]  # Maximum 5 insights
                else:
                    logger.warning(f"Insights extraction failed: {response.status}")
                    return ["Key insights could not be extracted"]
                    
        except Exception as e:
            logger.warning(f"Insights extraction failed: {e}")
            return ["Key insights could not be extracted"]
    
    async def health_check(self) -> str:
        """Check the health of the LLM service"""
        try:
            if not self.is_initialized:
                return "not_initialized"
            
            # Quick test request
            test_prompt = "Hello, respond with 'OK' if you're working."
            request_data = {
                "model": self.model_name,
                "prompt": test_prompt,
                "stream": False,
                "options": {
                    "num_predict": 10
                }
            }
            
            async with self.session.post(
                f"{self.host}/api/generate",
                json=request_data
            ) as response:
                if response.status == 200:
                    return "healthy"
                else:
                    return f"unhealthy_status_{response.status}"
                    
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return f"unhealthy_error"
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            async with self.session.post(
                f"{self.host}/api/show",
                json={"name": self.model_name}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "name": self.model_name,
                        "version": "1.0.0",  # Default version
                        "size": data.get("size", "unknown"),
                        "quantization": self.model_config.get("quantization", "4bit"),
                        "context_window": self.context_window,
                        "status": "active",
                        "last_updated": None
                    }
                else:
                    return {
                        "name": self.model_name,
                        "version": "unknown",
                        "status": "error",
                        "context_window": self.context_window
                    }
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {
                "name": self.model_name,
                "version": "unknown", 
                "status": "error",
                "context_window": self.context_window
            }
    
    async def close(self):
        """Close the LLM service and cleanup resources"""
        if self.session:
            await self.session.close()
            logger.info("LLM service closed") 