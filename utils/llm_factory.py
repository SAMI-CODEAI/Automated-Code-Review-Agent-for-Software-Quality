"""
LLM Factory - Create LLM instances based on provider configuration
"""

import os
from typing import Optional
from langchain_core.language_models import BaseChatModel
from utils.logger import get_logger

logger = get_logger(__name__)


def create_llm(
    model_name: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 8192
) -> BaseChatModel:
    """
    Create an LLM instance based on the configured provider.
    
    Args:
        model_name: Model name (uses env default if None)
        temperature: LLM temperature (lower = more focused)
        max_tokens: Maximum tokens per request
        
    Returns:
        Configured LLM instance (ChatGoogleGenerativeAI or ChatOllama)
        
    Raises:
        ValueError: If provider is invalid or required config is missing
    """
    provider = os.getenv('LLM_PROVIDER', 'gemini').lower()
    
    if provider == 'ollama':
        return _create_ollama_llm(model_name, temperature, max_tokens)
    elif provider == 'gemini':
        return _create_gemini_llm(model_name, temperature, max_tokens)
    else:
        raise ValueError(
            f"Invalid LLM_PROVIDER: {provider}. Must be 'gemini' or 'ollama'"
        )


def _create_ollama_llm(
    model_name: Optional[str],
    temperature: float,
    max_tokens: int
) -> BaseChatModel:
    """Create Ollama LLM instance."""
    try:
        from langchain_ollama import ChatOllama
    except ImportError:
        raise ImportError(
            "langchain-ollama not installed. "
            "Install with: pip install langchain-ollama"
        )
    
    model = model_name or os.getenv('OLLAMA_MODEL', 'llama3.2')
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    logger.info(f"🤖 Initializing Ollama LLM: {model} at {base_url}")
    
    try:
        llm = ChatOllama(
            model=model,
            base_url=base_url,
            temperature=temperature,
            num_predict=max_tokens,
        )
        return llm
    except Exception as e:
        logger.error(f"❌ Failed to initialize Ollama LLM: {str(e)}")
        raise


def _create_openai_llm(
    model_name: Optional[str],
    temperature: float,
    max_tokens: int
) -> BaseChatModel:
    """Create OpenAI LLM instance."""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        raise ImportError(
            "langchain-openai not installed. "
            "Install with: pip install langchain-openai"
        )
    
    model = model_name or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == 'your_openai_api_key_here':
        raise ValueError(
            "OPENAI_API_KEY not set. Please configure .env file with your API key."
        )
        
    logger.info(f"🤖 Initializing OpenAI LLM: {model}")
    
    try:
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key
        )
        return llm
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI LLM: {str(e)}")
        raise


def _create_gemini_llm(
    model_name: Optional[str],
    temperature: float,
    max_tokens: int
) -> BaseChatModel:
    """Create Google Gemini LLM instance."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError:
        raise ImportError(
            "langchain-google-genai not installed. "
            "Install with: pip install langchain-google-genai"
        )
    
    model = model_name or os.getenv('GEMINI_MODEL', 'gemini-1.5-flash-latest')
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key or api_key == 'your_gemini_api_key_here':
        raise ValueError(
            "GOOGLE_API_KEY not set. Please configure .env file with your API key."
        )
    
    logger.info(f"🤖 Initializing Gemini LLM: {model}")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            max_output_tokens=max_tokens,
            google_api_key=api_key
        )
        
        try:
            openai_fallback = _create_openai_llm(None, temperature, max_tokens)
            ollama_fallback = _create_ollama_llm(None, temperature, max_tokens)
            llm_with_fallback = llm.with_fallbacks(
                [openai_fallback, ollama_fallback],
                exceptions_to_handle=(Exception,)
            )
            logger.info("🛡️ Added OpenAI and Ollama as automatic fallbacks for Gemini")
            return llm_with_fallback
        except Exception as fallback_error:
            logger.warning(f"⚠️ Could not setup fallbacks: {str(fallback_error)}")
            return llm
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini LLM: {str(e)}")
        raise
