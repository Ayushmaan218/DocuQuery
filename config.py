import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/docuquery')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Upload Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    VECTOR_STORE_PATH = os.getenv('VECTOR_STORE_PATH', 'vector_store')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'pdf,docx,txt').split(','))
    
    # RAG Configuration
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))
    TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', 3))
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', 0.7))
    
    # Embedding model
    EMBEDDING_MODEL = 'text-embedding-3-small'
    
    # LLM model
    LLM_MODEL = 'gpt-4'
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in .env file")
        
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.VECTOR_STORE_PATH, exist_ok=True)
        
        return True
