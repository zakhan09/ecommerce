from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def create_database_if_not_exists():
    """
    Check if the database exists, if not create it.
    This function handles database creation for different database types.
    """
    try:
        if not database_exists(engine.url):
            logger.info(f"Database does not exist. Creating database: {engine.url}")
            create_database(engine.url)
            logger.info("Database created successfully!")
        else:
            logger.info("Database already exists.")
        
        test_connection()
        return True
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False

def init_database():
    """
    Initialize the database - create if not exists and create all tables.
    This function should be called on app startup.
    """
    try:
        if create_database_if_not_exists():
            return True
        else:
            logger.error("Failed to create database")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False