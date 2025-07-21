"""
Worker modules for specialized task processing.

Workers are automatically registered when imported.
"""

# Import all workers to trigger registration
from .travel import TravelWorker
from .finance import FinanceWorker

__all__ = ["TravelWorker", "FinanceWorker"]