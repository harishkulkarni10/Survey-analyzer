"""
Configuration management for Survey Analyzer
"""

import os
from datetime import datetime
from typing import Optional


class Config:
    """Configuration settings for Survey Analyzer"""
    
    # Base output directory
    BASE_OUTPUT_DIR = "./outputs"
    
    # Gemini API Key - loaded from api_key.py file
    @staticmethod
    def get_gemini_api_key() -> Optional[str]:
        """Load Gemini API key from api_key.py"""
        try:
            import sys
            # Add parent directory so we can import api_key
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            from api_key import GEMINI_API_KEY
            return GEMINI_API_KEY if GEMINI_API_KEY else None
        except (ImportError, Exception):
            return None
    
    # Create timestamped output directory
    @classmethod
    def get_timestamped_output_dir(cls) -> str:
        """Get timestamped output directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(cls.BASE_OUTPUT_DIR, f"analysis_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    # Visualization settings
    FIGURE_SIZE = (16, 12)
    DPI = 300
    
    # Analysis settings
    DEFAULT_SAMPLE_SIZE = 150
