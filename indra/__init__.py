"""
Indra MVP - AI Agent Orchestration Framework

A file-based agent orchestration system that follows the Queen → Router → Workers → Compiler pattern.
Designed for simplicity and demonstration purposes.
"""

__version__ = "0.1.0"
__author__ = "Mehul - Five Labs"

from .queen import Queen
from .router import Router
from .compiler import Compiler
from .base_worker import BaseWorker, register_worker, WORKER_REGISTRY

__all__ = [
    "Queen",
    "Router", 
    "Compiler",
    "BaseWorker",
    "register_worker",
    "WORKER_REGISTRY"
]