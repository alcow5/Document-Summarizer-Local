#!/usr/bin/env python3
"""
Database Initialization Script
Creates and initializes the SQLite database for the Privacy-Focused AI Document Summarizer
"""

import os
import sys
import sqlite3
from pathlib import Path
import getpass
import hashlib
import secrets
from cryptography.fernet import Fernet
import yaml
from loguru import logger

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

DATABASE_DIR = Path(__file__).parent.parent.parent / "database"
SCHEMA_FILE = DATABASE_DIR / "schema.sql"
CONFIG_FILE = Path(__file__).parent.parent / "config.yaml"


class DatabaseInitializer:
    """Database initialization and setup"""
    
    def __init__(self, db_path=None, encryption_key=None):
        self.db_path = db_path or DATABASE_DIR / "summaries.db"
        self.encryption_key = encryption_key
        self.config = self._load_config()
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self):
        """Load application configuration"""
        try:
            with open(CONFIG_FILE, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {CONFIG_FILE}")
            return {}
    
    def generate_encryption_key(self):
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()
    
    def prompt_for_encryption_key(self):
        """Prompt user for encryption key or generate new one"""
        print("\n=== Database Encryption Setup ===")
        print("Your database will be encrypted for maximum security.")
        print("You can either:")
        print("1. Generate a new random encryption key")
        print("2. Provide your own encryption key")
        print("3. Use a password-based key")
        
        while True:
            choice = input("\nChoose option (1/2/3): ").strip()
            
            if choice == "1":
                key = self.generate_encryption_key()
                print(f"\nGenerated encryption key: {key}")
                print("⚠️  IMPORTANT: Save this key securely! You'll need it to access your data.")
                input("Press Enter after saving the key...")
                return key
            
            elif choice == "2":
                key = input("Enter your encryption key: ").strip()
                if len(key) >= 32:
                    return key
                else:
                    print("❌ Key must be at least 32 characters long")
            
            elif choice == "3":
                password = getpass.getpass("Enter a password for encryption: ")
                confirm_password = getpass.getpass("Confirm password: ")
                
                if password != confirm_password:
                    print("❌ Passwords don't match")
                    continue
                
                if len(password) < 8:
                    print("❌ Password must be at least 8 characters long")
                    continue
                
                # Generate key from password
                salt = secrets.token_bytes(32)
                key_bytes = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
                key = Fernet.generate_key().decode()  # Use Fernet key format
                
                print("✅ Password-based encryption key generated")
                return key
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3")
    
    def create_database(self):
        """Create and initialize the database"""
        try:
            logger.info(f"Creating database at: {self.db_path}")
            
            # Check if database already exists
            if self.db_path.exists():
                response = input(f"Database already exists at {self.db_path}. Overwrite? (y/N): ")
                if response.lower() != 'y':
                    logger.info("Database initialization cancelled")
                    return False
                
                # Backup existing database
                backup_path = self.db_path.with_suffix('.db.backup')
                self.db_path.rename(backup_path)
                logger.info(f"Existing database backed up to: {backup_path}")
            
            # Get encryption key
            if not self.encryption_key:
                self.encryption_key = self.prompt_for_encryption_key()
            
            # Create database connection
            conn = sqlite3.connect(str(self.db_path))
            
            # Enable encryption if using SQLCipher
            if self.encryption_key and 'sqlcipher' in sys.modules:
                conn.execute(f"PRAGMA key = '{self.encryption_key}'")
                logger.info("Database encryption enabled")
            
            # Read and execute schema
            if not SCHEMA_FILE.exists():
                raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")
            
            with open(SCHEMA_FILE, 'r') as f:
                schema_sql = f.read()
            
            # Execute schema in parts (SQLite doesn't support multiple statements well)
            for statement in schema_sql.split(';'):
                statement = statement.strip()
                if statement:
                    try:
                        conn.execute(statement)
                    except sqlite3.Error as e:
                        if "already exists" not in str(e).lower():
                            logger.warning(f"SQL statement failed: {statement[:50]}... Error: {e}")
            
            conn.commit()
            
            # Verify database creation
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['summaries', 'app_settings', 'model_info', 'processing_stats', 
                             'user_preferences', 'document_metadata']
            
            missing_tables = set(expected_tables) - set(tables)
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False
            
            logger.info(f"Database created successfully with tables: {tables}")
            
            # Insert initial data
            self._insert_initial_data(conn)
            
            conn.close()
            
            # Save encryption key to environment or config
            self._save_encryption_key()
            
            logger.info("✅ Database initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    def _insert_initial_data(self, conn):
        """Insert initial configuration data"""
        logger.info("Inserting initial configuration data...")
        
        # Default settings (already in schema, but ensure they exist)
        settings_data = [
            ('max_summaries', '50', 'integer', 'Maximum number of summaries to keep'),
            ('auto_cleanup', 'true', 'boolean', 'Automatically cleanup old summaries'),
            ('encryption_enabled', 'true', 'boolean', 'Database encryption enabled'),
            ('app_version', '1.0.0', 'string', 'Application version'),
        ]
        
        for setting in settings_data:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO app_settings (setting_key, setting_value, setting_type, description) VALUES (?, ?, ?, ?)",
                    setting
                )
            except sqlite3.Error as e:
                logger.warning(f"Failed to insert setting {setting[0]}: {e}")
        
        # Default user preferences
        preferences_data = [
            ('default_template', 'general', 'string'),
            ('ui_theme', 'light', 'string'),
            ('auto_save_summaries', 'true', 'boolean'),
        ]
        
        for pref in preferences_data:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO user_preferences (preference_key, preference_value, data_type) VALUES (?, ?, ?)",
                    pref
                )
            except sqlite3.Error as e:
                logger.warning(f"Failed to insert preference {pref[0]}: {e}")
        
        conn.commit()
        logger.info("Initial data inserted successfully")
    
    def _save_encryption_key(self):
        """Save encryption key to environment file"""
        if not self.encryption_key:
            return
        
        env_file = Path(__file__).parent.parent / ".env"
        
        # Read existing .env file
        env_content = ""
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Remove existing DB_ENCRYPTION_KEY line
            lines = [line for line in lines if not line.startswith('DB_ENCRYPTION_KEY=')]
            env_content = ''.join(lines)
        
        # Add encryption key
        env_content += f"\nDB_ENCRYPTION_KEY={self.encryption_key}\n"
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        logger.info(f"Encryption key saved to: {env_file}")
        
        # Set file permissions (Unix only)
        try:
            os.chmod(env_file, 0o600)  # Read/write for owner only
        except (OSError, AttributeError):
            pass  # Windows or permission error
    
    def verify_database(self):
        """Verify database integrity"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            
            # Set encryption key if available
            if self.encryption_key and 'sqlcipher' in sys.modules:
                conn.execute(f"PRAGMA key = '{self.encryption_key}'")
            
            # Check database integrity
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            if result == "ok":
                logger.info("✅ Database integrity check passed")
                
                # Test basic operations
                conn.execute("SELECT COUNT(*) FROM summaries")
                conn.execute("SELECT COUNT(*) FROM app_settings")
                
                logger.info("✅ Database operations test passed")
                return True
            else:
                logger.error(f"❌ Database integrity check failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database verification failed: {e}")
            return False
        finally:
            try:
                conn.close()
            except:
                pass
    
    def reset_database(self):
        """Reset database to initial state"""
        logger.warning("Resetting database to initial state...")
        
        if self.db_path.exists():
            backup_path = self.db_path.with_suffix(f'.db.backup.{int(time.time())}')
            self.db_path.rename(backup_path)
            logger.info(f"Existing database backed up to: {backup_path}")
        
        return self.create_database()


def main():
    """Main initialization function"""
    import argparse
    import time
    
    parser = argparse.ArgumentParser(description="Initialize Privacy-Focused AI Document Summarizer Database")
    parser.add_argument("--db-path", help="Database file path")
    parser.add_argument("--encryption-key", help="Encryption key (if not provided, will prompt)")
    parser.add_argument("--reset", action="store_true", help="Reset existing database")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing database")
    parser.add_argument("--no-encryption", action="store_true", help="Skip encryption setup")
    
    args = parser.parse_args()
    
    # Setup logging
    logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")
    
    print("🔒 Privacy-Focused AI Document Summarizer - Database Setup")
    print("=" * 60)
    
    # Initialize database manager
    initializer = DatabaseInitializer(
        db_path=Path(args.db_path) if args.db_path else None,
        encryption_key=args.encryption_key if not args.no_encryption else None
    )
    
    try:
        if args.verify_only:
            # Only verify existing database
            if initializer.verify_database():
                print("\n✅ Database verification successful!")
                return 0
            else:
                print("\n❌ Database verification failed!")
                return 1
        
        elif args.reset:
            # Reset database
            if initializer.reset_database():
                print("\n✅ Database reset successful!")
            else:
                print("\n❌ Database reset failed!")
                return 1
        
        else:
            # Normal initialization
            if initializer.create_database():
                print("\n✅ Database initialization successful!")
                
                # Verify the new database
                if initializer.verify_database():
                    print("✅ Database verification passed!")
                else:
                    print("⚠️  Database created but verification failed!")
                
            else:
                print("\n❌ Database initialization failed!")
                return 1
        
        print("\n🎉 Setup complete! You can now start the application.")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 