"""Router - Task dispatch and monitoring."""

import json
import time
from typing import List, Dict
from pathlib import Path
from .models import Task, TaskStatus
from .base_worker import get_worker_class


class Router:
    """Dispatches tasks and monitors execution."""
    
    def __init__(self, queue_dir: str = "queue", results_dir: str = "results"):
        self.queue_dir = Path(queue_dir)
        self.results_dir = Path(results_dir)
        
        # Ensure directories exist
        self.queue_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
    
    def dispatch_tasks(self, tasks: List[Task]) -> None:
        """Create task files in queue directory."""
        if not tasks:
            return
            
        for task in tasks:
            try:
                task_file = self.queue_dir / f"{task.id}.json"
                with open(task_file, 'w') as f:
                    json.dump(task.dict(), f, indent=2)
            except (OSError, IOError) as e:
                print(f"Error dispatching task {task.id}: {e}")
                continue
    
    def monitor_progress(self) -> Dict[str, str]:
        """Check status of all tasks."""
        progress = {}
        for task_file in self.queue_dir.glob("*.json"):
            try:
                with open(task_file, 'r') as f:
                    task_data = json.load(f)
                
                task_id = task_data.get('id')
                if task_id:
                    progress[task_id] = task_data.get('status', 'PENDING')
            except (json.JSONDecodeError, KeyError, OSError):
                # Skip malformed or unreadable files
                continue
        return progress
    
    def is_complete(self, task_ids: List[str]) -> bool:
        """Check if all tasks are done."""
        if not task_ids:
            return True
            
        progress = self.monitor_progress()
        return all(progress.get(tid) == TaskStatus.DONE.value for tid in task_ids)
    
    def execute_pending_tasks(self) -> None:
        """Execute all pending tasks."""
        for task_file in self.queue_dir.glob("*.json"):
            try:
                with open(task_file, 'r') as f:
                    task_data = json.load(f)
                
                if task_data.get('status') != TaskStatus.PENDING.value:
                    continue
                
                worker_name = task_data.get('worker')
                if not worker_name:
                    continue
                
                worker_class = get_worker_class(worker_name)
                worker = worker_class(worker_name, str(self.results_dir))
                worker.process_task_file(str(task_file))
                
            except (json.JSONDecodeError, KeyError, OSError):
                # Skip malformed or unreadable files
                continue
            except Exception as e:
                print(f"Error executing task from {task_file}: {e}")
                continue
    
    def wait_for_completion(self, task_ids: List[str], timeout: int = 30) -> bool:
        """Wait for tasks to complete with timeout."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_complete(task_ids):
                return True
            self.execute_pending_tasks()
            time.sleep(1)
        
        return False