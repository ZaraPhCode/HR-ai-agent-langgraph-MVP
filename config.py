"""
Configuration management for the HR Agent.
Supports environment variables with fallbacks.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the HR Agent"""
    
    # LLM Provider: 'openai', 'claude', 'groq', or 'mock'
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'groq')
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # Model names for each provider
    MODELS = {
        'openai': 'gpt-4o-mini',
        'claude': 'claude-3-5-sonnet-20241022',
        # 'groq': 'openai/gpt-oss-120b',
        'mock': 'mock-model'
    }
    
    # Temperature and max tokens
    TEMPERATURE = 0.3
    MAX_TOKENS = 800
    
    # File paths
    INPUT_FILE = os.getenv('INPUT_FILE', 'input.csv')
    RESULTS_FILE = os.getenv('RESULTS_FILE', 'results.csv')
    
    @classmethod
    def get_model(cls) -> str:
        """Get the model name for the current provider"""
        return cls.MODELS.get(cls.LLM_PROVIDER, 'gpt-4o-mini')
    
    @classmethod
    def get_api_key(cls) -> str:
        """Get the API key for the current provider"""
        key_map = {
            'openai': cls.OPENAI_API_KEY,
            'claude': cls.CLAUDE_API_KEY,
            'groq': cls.GROQ_API_KEY,
            'mock': 'mock-key'
        }
        return key_map.get(cls.LLM_PROVIDER, '')
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if the current provider is properly configured"""
        if cls.LLM_PROVIDER == 'mock':
            return True
        return bool(cls.get_api_key())