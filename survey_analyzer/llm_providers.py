"""
LLM Provider for Survey Analyzer
Uses Google Gemini Flash 2.5 API
"""

from abc import ABC, abstractmethod
from typing import Optional

from .config import Config


# Check if Gemini library is installed
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self):
        self.name = "Base"
        self.available = False
    
    @abstractmethod
    def generate(self, prompt: str) -> Optional[str]:
        """Generate response from LLM"""
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Flash 2.5 API provider"""
    
    def __init__(self):
        super().__init__()
        self.name = "Google Gemini Flash 2.5"
        self.api_key = Config.get_gemini_api_key()
        self.model = None
        
        if not GEMINI_AVAILABLE:
            print("   ❌ google-generativeai not installed. Run: pip install google-generativeai")
            self.available = False
            return
        
        if not self.api_key:
            print("   ❌ Gemini API key not set. Add your key in api_key.py")
            self.available = False
            return
        
        # Configure and initialize
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash")
            self.available = True
            print("   ✅ Gemini Flash 2.5 initialized successfully")
        except Exception as e:
            print(f"   ❌ Gemini initialization error: {e}")
            self.available = False
    
    def generate(self, prompt: str) -> Optional[str]:
        """Generate response from Gemini"""
        if not self.available or self.model is None:
            return None
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2000,
                )
            )
            return response.text.strip() if response.text else None
        except Exception as e:
            print(f"⚠️  Gemini API error: {e}")
            return None


def get_llm_provider() -> GeminiProvider:
    """
    Initialize and return the Gemini LLM provider.
    
    Returns:
        GeminiProvider instance
        
    Raises:
        RuntimeError if Gemini is not available
    """
    provider = GeminiProvider()
    
    if provider.available:
        print(f"✅ Using {provider.name}")
        return provider
    
    # Not available - show clear instructions
    raise RuntimeError(
        "\n❌ GEMINI NOT AVAILABLE!\n"
        "\nTo fix this:\n"
        "  1. Install the package:  pip install google-generativeai\n"
        "  2. Open api_key.py and paste your Gemini API key\n"
        "\nThat's it. Then run main.py again.\n"
    )
