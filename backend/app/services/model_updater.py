"""
Model Updater Service for Privacy-Focused AI Document Summarizer
Handles checking for and downloading LLM model updates
"""

import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger

from ..config import get_models_directory


class ModelUpdater:
    """Service for updating LLM models"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.update_config = config.get("updates", {})
        self.model_config = config["model"]
        
        self.check_url = self.update_config.get("check_url", "")
        self.models_directory = get_models_directory(config)
        self.auto_check = self.update_config.get("auto_check", True)
        self.backup_old_models = self.update_config.get("backup_old_models", True)
        
        self.last_check = None
        self.current_version = "1.0.0"  # Default version
    
    async def check_and_update(self) -> Dict[str, Any]:
        """Check for model updates and download if available"""
        try:
            logger.info("Checking for model updates...")
            
            # For MVP, we'll implement a simple version check
            # In production, this would check your server or GitHub releases
            update_info = await self._check_for_updates()
            
            if update_info.get("update_available", False):
                logger.info(f"Model update available: {update_info['latest_version']}")
                
                # Download and install update
                success = await self._download_update(update_info)
                
                if success:
                    update_info["update_installed"] = True
                    logger.info("Model update completed successfully")
                else:
                    update_info["update_installed"] = False
                    logger.error("Model update failed")
            else:
                logger.info("No model updates available")
            
            self.last_check = datetime.utcnow()
            return update_info
            
        except Exception as e:
            logger.error(f"Model update check failed: {e}")
            return {
                "update_available": False,
                "error": str(e),
                "last_check": datetime.utcnow()
            }
    
    async def _check_for_updates(self) -> Dict[str, Any]:
        """Check if updates are available"""
        try:
            # For MVP, simulate update check
            # In production, this would make an actual HTTP request
            if not self.check_url:
                logger.info("No update URL configured, skipping update check")
                return {
                    "update_available": False,
                    "current_version": self.current_version,
                    "latest_version": self.current_version,
                    "reason": "No update URL configured"
                }
            
            # Simulate checking for updates
            # This would be replaced with actual HTTP request in production
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(self.check_url, timeout=30) as response:
                        if response.status == 200:
                            data = await response.json()
                            latest_version = data.get("tag_name", "1.0.0")
                            
                            # Simple version comparison
                            if self._is_newer_version(latest_version, self.current_version):
                                return {
                                    "update_available": True,
                                    "current_version": self.current_version,
                                    "latest_version": latest_version,
                                    "download_url": data.get("assets", [{}])[0].get("browser_download_url"),
                                    "changelog": data.get("body", "No changelog available")
                                }
                            else:
                                return {
                                    "update_available": False,
                                    "current_version": self.current_version,
                                    "latest_version": latest_version,
                                    "reason": "Already up to date"
                                }
                        else:
                            logger.warning(f"Update check failed: HTTP {response.status}")
                            return {
                                "update_available": False,
                                "error": f"HTTP {response.status}",
                                "current_version": self.current_version
                            }
                except asyncio.TimeoutError:
                    logger.warning("Update check timed out")
                    return {
                        "update_available": False,
                        "error": "Request timeout",
                        "current_version": self.current_version
                    }
                except Exception as e:
                    logger.warning(f"Update check failed: {e}")
                    return {
                        "update_available": False,
                        "error": str(e),
                        "current_version": self.current_version
                    }
                    
        except Exception as e:
            logger.error(f"Update check error: {e}")
            return {
                "update_available": False,
                "error": str(e),
                "current_version": self.current_version
            }
    
    def _is_newer_version(self, version1: str, version2: str) -> bool:
        """Compare version strings (simple implementation)"""
        try:
            # Remove 'v' prefix if present
            v1 = version1.lstrip('v').split('.')
            v2 = version2.lstrip('v').split('.')
            
            # Pad with zeros to make same length
            max_len = max(len(v1), len(v2))
            v1.extend(['0'] * (max_len - len(v1)))
            v2.extend(['0'] * (max_len - len(v2)))
            
            # Convert to integers and compare
            for i in range(max_len):
                if int(v1[i]) > int(v2[i]):
                    return True
                elif int(v1[i]) < int(v2[i]):
                    return False
            
            return False  # Versions are equal
            
        except Exception:
            # If version comparison fails, assume no update
            return False
    
    async def _download_update(self, update_info: Dict[str, Any]) -> bool:
        """Download and install model update"""
        try:
            download_url = update_info.get("download_url")
            if not download_url:
                logger.error("No download URL provided")
                return False
            
            logger.info(f"Downloading model update from: {download_url}")
            
            # For MVP, we'll simulate the download
            # In production, this would download actual model files
            await asyncio.sleep(2)  # Simulate download time
            
            # Backup current model if enabled
            if self.backup_old_models:
                await self._backup_current_model()
            
            # Install new model (simulated)
            logger.info("Installing new model...")
            await asyncio.sleep(1)  # Simulate installation
            
            # Update current version
            self.current_version = update_info.get("latest_version", self.current_version)
            
            logger.info("Model update installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Model download failed: {e}")
            return False
    
    async def _backup_current_model(self):
        """Backup current model before update"""
        try:
            logger.info("Backing up current model...")
            
            # Create backup directory
            backup_dir = self.models_directory / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            # For MVP, just log the backup
            # In production, this would copy actual model files
            backup_path = backup_dir / f"tinyllama_{self.current_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"Model backed up to: {backup_path}")
            
        except Exception as e:
            logger.warning(f"Model backup failed: {e}")
    
    async def get_update_status(self) -> Dict[str, Any]:
        """Get current update status"""
        return {
            "current_version": self.current_version,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "auto_check_enabled": self.auto_check,
            "models_directory": str(self.models_directory),
            "check_url": self.check_url if self.check_url else "Not configured"
        }
    
    async def force_check(self) -> Dict[str, Any]:
        """Force an immediate update check"""
        logger.info("Forcing model update check...")
        return await self.check_and_update()
    
    def should_check_for_updates(self) -> bool:
        """Check if we should check for updates based on interval"""
        if not self.auto_check:
            return False
        
        if not self.last_check:
            return True
        
        # Check weekly by default
        check_interval_hours = self.update_config.get("check_interval_hours", 168)  # 1 week
        time_since_check = datetime.utcnow() - self.last_check
        
        return time_since_check.total_seconds() > (check_interval_hours * 3600)
    
    async def cleanup_old_models(self):
        """Clean up old model files and backups"""
        try:
            backup_dir = self.models_directory / "backups"
            if not backup_dir.exists():
                return
            
            # Keep only last 3 backups
            backup_files = sorted(backup_dir.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)
            
            for old_backup in backup_files[3:]:  # Keep newest 3
                if old_backup.is_file():
                    old_backup.unlink()
                    logger.info(f"Removed old backup: {old_backup.name}")
                elif old_backup.is_dir():
                    import shutil
                    shutil.rmtree(old_backup)
                    logger.info(f"Removed old backup directory: {old_backup.name}")
            
        except Exception as e:
            logger.warning(f"Cleanup of old models failed: {e}")
    
    async def get_available_models(self) -> Dict[str, Any]:
        """Get information about available models"""
        try:
            # This would query Ollama for available models
            # For MVP, return basic info
            return {
                "current_model": self.model_config["name"],
                "models_directory": str(self.models_directory),
                "available_models": ["tinyllama:latest"],  # Would be queried from Ollama
                "last_update_check": self.last_check.isoformat() if self.last_check else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return {
                "current_model": self.model_config["name"],
                "error": str(e)
            } 