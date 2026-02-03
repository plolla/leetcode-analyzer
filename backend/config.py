import os
from dotenv import load_dotenv
from enum import Enum

# Load environment variables
load_dotenv()


class AIProvider(str, Enum):
    CLAUDE = "claude"
    OPENAI = "openai"


class Config:
    """Application configuration."""
    
    # AI Service Configuration
    AI_PROVIDER = os.getenv("AI_PROVIDER", AIProvider.CLAUDE.value)
    FALLBACK_PROVIDER = os.getenv("FALLBACK_PROVIDER", AIProvider.OPENAI.value)
    
    # Claude Configuration
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini-2025-08-07")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    
    @classmethod
    def get_ai_provider(cls) -> AIProvider:
        """Get the configured AI provider."""
        try:
            return AIProvider(cls.AI_PROVIDER.lower())
        except ValueError:
            return AIProvider.CLAUDE
    
    @classmethod
    def get_fallback_provider(cls) -> AIProvider:
        """Get the configured fallback AI provider."""
        try:
            return AIProvider(cls.FALLBACK_PROVIDER.lower())
        except ValueError:
            return AIProvider.OPENAI
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        provider = cls.get_ai_provider()
        
        if provider == AIProvider.CLAUDE:
            return bool(cls.CLAUDE_API_KEY)
        elif provider == AIProvider.OPENAI:
            return bool(cls.OPENAI_API_KEY)
        
        return False


config = Config()
