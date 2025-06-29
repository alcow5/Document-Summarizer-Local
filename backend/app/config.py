"""
Configuration management for Privacy-Focused AI Document Summarizer
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger

# Default configuration path
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
ENV_PATH = Path(__file__).parent.parent / ".env"


def load_env_variables():
    """Load environment variables from .env file"""
    if ENV_PATH.exists():
        with open(ENV_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    os.environ[key.strip()] = value.strip()


def load_config(config_path: Path = CONFIG_PATH) -> Dict[str, Any]:
    """
    Load application configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        # Load environment variables first
        load_env_variables()
        
        # Load YAML configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Override with environment variables where applicable
        config = _apply_env_overrides(config)
        
        # Validate configuration
        _validate_config(config)
        
        logger.info(f"Configuration loaded from {config_path}")
        return config
        
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to configuration"""
    
    # Database encryption key
    if os.getenv('DB_ENCRYPTION_KEY'):
        config.setdefault('database', {})['encryption_key'] = os.getenv('DB_ENCRYPTION_KEY')
    
    # Ollama host
    if os.getenv('OLLAMA_HOST'):
        config.setdefault('model', {})['host'] = os.getenv('OLLAMA_HOST')
    
    # Log level
    if os.getenv('LOG_LEVEL'):
        config.setdefault('logging', {})['level'] = os.getenv('LOG_LEVEL')
    
    # Debug mode
    if os.getenv('DEBUG'):
        config.setdefault('app', {})['debug'] = os.getenv('DEBUG').lower() in ('true', '1', 'yes')
    
    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration has required sections and values"""
    
    required_sections = ['app', 'database', 'model', 'documents', 'templates']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate app section
    app_config = config['app']
    required_app_keys = ['name', 'version', 'host', 'port']
    for key in required_app_keys:
        if key not in app_config:
            raise ValueError(f"Missing required app configuration: {key}")
    
    # Validate database section
    db_config = config['database']
    if 'path' not in db_config:
        raise ValueError("Missing database path configuration")
    
    # Validate model section
    model_config = config['model']
    required_model_keys = ['name', 'host']
    for key in required_model_keys:
        if key not in model_config:
            raise ValueError(f"Missing required model configuration: {key}")
    
    # Validate templates exist
    templates = config['templates']
    if not templates:
        raise ValueError("No summary templates configured")
    
    logger.info("Configuration validation passed")


def get_database_path(config: Dict[str, Any]) -> Path:
    """Get the absolute path to the database file"""
    db_path = config['database']['path']
    
    # If relative path, make it relative to project root
    if not Path(db_path).is_absolute():
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / db_path
    
    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    return Path(db_path)


def get_models_directory(config: Dict[str, Any]) -> Path:
    """Get the models directory path"""
    models_dir = config.get('updates', {}).get('models_directory', 'models/')
    
    # If relative path, make it relative to project root
    if not Path(models_dir).is_absolute():
        project_root = Path(__file__).parent.parent.parent
        models_dir = project_root / models_dir
    
    # Ensure directory exists
    Path(models_dir).mkdir(parents=True, exist_ok=True)
    
    return Path(models_dir)


def get_logs_directory(config: Dict[str, Any]) -> Path:
    """Get the logs directory path"""
    log_file = config.get('logging', {}).get('file', 'logs/app.log')
    log_path = Path(log_file)
    
    # If relative path, make it relative to project root
    if not log_path.is_absolute():
        project_root = Path(__file__).parent.parent.parent
        log_path = project_root / log_path
    
    # Ensure directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    return log_path 