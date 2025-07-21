"""
Base worker infrastructure and registry system.

Provides the foundation for all specialized workers with automatic registration
and standardized task processing.
"""

import json
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from datetime import datetime

# Global worker registry
WORKER_REGISTRY: Dict[str, Type['BaseWorker']] = {}

logger = logging.getLogger(__name__)


def register_worker(name: str):
    """
    Decorator for automatic worker registration.
    
    Args:
        name: Unique identifier for the worker
        
    Raises:
        ValueError: If worker name already exists in registry
    """
    def decorator(cls):
        if name in WORKER_REGISTRY:
            raise ValueError(f"Worker '{name}' already registered. Choose a unique name.")
        
        WORKER_REGISTRY[name] = cls
        logger.info(f"Registered worker: {name}")
        return cls
    
    return decorator


class BaseWorker(ABC):
    """
    Abstract base class for all workers.
    
    Provides standardized task processing workflow and common functionality.
    All workers must inherit from this class and implement the execute method.
    """
    
    def __init__(self, worker_name: str, results_dir: str = "results"):
        """
        Initialize the worker.
        
        Args:
            worker_name: Unique identifier for this worker instance
            results_dir: Directory where to write result files
        """
        self.worker_name = worker_name
        self.results_dir = results_dir
        self.logger = logging.getLogger(f"{__name__}.{worker_name}")
    
    @abstractmethod
    def execute(self, **inputs) -> Dict[str, Any]:
        """
        Execute the worker's specialized functionality.
        
        This method must be implemented by all subclasses.
        
        Args:
            **inputs: Task-specific input parameters
            
        Returns:
            Dictionary containing the worker's output
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement the execute method")
    
    def process_task_file(self, task_file_path: str) -> None:
        """
        Standard task processing workflow.
        
        Reads task file, executes the task, and writes results.
        
        Args:
            task_file_path: Path to the task JSON file
            
        Raises:
            FileNotFoundError: If task file doesn't exist
            json.JSONDecodeError: If task file contains invalid JSON
            Exception: If task execution fails
        """
        try:
            # Read and parse task file
            with open(task_file_path, 'r') as f:
                task_data = json.load(f)
            
            task_id = task_data['id']
            inputs = task_data.get('inputs', {})
            
            self.logger.info(f"Processing task {task_id}")
            
            # Update task status to IN_PROGRESS
            task_data['status'] = 'IN_PROGRESS'
            task_data['started_at'] = datetime.utcnow().isoformat()
            
            with open(task_file_path, 'w') as f:
                json.dump(task_data, f, indent=2)
            
            # Execute the task
            start_time = datetime.utcnow()
            outputs = self.execute(**inputs)
            end_time = datetime.utcnow()
            
            # Create result data
            result_data = {
                'task_id': task_id,
                'worker': self.worker_name,
                'outputs': outputs,
                'execution_time': (end_time - start_time).total_seconds(),
                'timestamp': end_time.isoformat()
            }
            
            # Write result to results directory
            os.makedirs(self.results_dir, exist_ok=True)
            result_path = os.path.join(self.results_dir, f"{task_id}_result.json")
            
            with open(result_path, 'w') as f:
                json.dump(result_data, f, indent=2)
            
            # Update task status to DONE
            task_data['status'] = 'DONE'
            task_data['completed_at'] = end_time.isoformat()
            task_data['result_path'] = result_path
            
            with open(task_file_path, 'w') as f:
                json.dump(task_data, f, indent=2)
            
            self.logger.info(f"Task {task_id} completed successfully")
            
        except FileNotFoundError:
            self.logger.error(f"Task file not found: {task_file_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in task file {task_file_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            # Update task status to ERROR
            try:
                with open(task_file_path, 'r') as f:
                    task_data = json.load(f)
                task_data['status'] = 'ERROR'
                task_data['error'] = str(e)
                task_data['failed_at'] = datetime.utcnow().isoformat()
                with open(task_file_path, 'w') as f:
                    json.dump(task_data, f, indent=2)
            except:
                pass  # Don't fail on error logging
            raise


def get_worker_class(worker_name: str) -> Type[BaseWorker]:
    """
    Get a worker class by name from the registry.
    
    Args:
        worker_name: Name of the worker to retrieve
        
    Returns:
        Worker class
        
    Raises:
        KeyError: If worker name not found in registry
    """
    # Ensure workers are imported
    _import_workers()
    
    if worker_name not in WORKER_REGISTRY:
        available_workers = list(WORKER_REGISTRY.keys())
        raise KeyError(f"Worker '{worker_name}' not found. Available workers: {available_workers}")
    
    return WORKER_REGISTRY[worker_name]


def list_available_workers() -> list[str]:
    """
    Get list of all registered worker names.
    
    Returns:
        List of worker names
    """
    # Ensure workers are imported
    _import_workers()
    return list(WORKER_REGISTRY.keys())


def _import_workers():
    """Import all workers to trigger registration."""
    try:
        from . import workers
    except ImportError:
        # Workers module not available
        pass