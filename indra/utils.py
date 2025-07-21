"""Simple utilities for Indra."""

import os
import logging
from pathlib import Path


def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def ensure_directories():
    """Create required directories."""
    for directory in ["queue", "results", "logs"]:
        Path(directory).mkdir(exist_ok=True)


def get_api_key():
    """Get OpenAI API key from environment."""
    return os.getenv("OPENAI_API_KEY")