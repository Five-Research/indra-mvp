"""
BeeScript DSL - Enhanced task definition language with dependencies and constraints.

Implements the mini-DSL described in the research paper for hierarchical task planning
with dependency resolution, budget constraints, and validation.
"""

import json
import uuid
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field, validator


class TaskStatus(str, Enum):
    """Enhanced task status for BeeScript execution."""
    PENDING = "PENDING"
    READY = "READY"  # Dependencies satisfied, ready to execute
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"  # Skipped due to dependency failure


@dataclass
class BeeScriptTask:
    """Enhanced task definition with dependencies and constraints."""
    id: str
    agent: str
    task: str
    params: Dict[str, Any] = field(default_factory=dict)
    after: List[str] = field(default_factory=list)  # Task dependencies
    cost_estimate: int = 10  # Estimated credit cost
    retry_max: int = 2  # Maximum retry attempts
    timeout_seconds: int = 30  # Task timeout
    status: TaskStatus = TaskStatus.PENDING
    actual_cost: int = 0  # Actual cost incurred
    retry_count: int = 0  # Current retry count
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


@dataclass 
class BeeScript:
    """Complete BeeScript workflow definition."""
    goal: str
    budget_credits: int
    timeout_minutes: int = 10
    subtasks: List[BeeScriptTask] = field(default_factory=list)
    
    # Runtime state
    total_cost: int = 0
    status: str = "PENDING"
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class BeeScriptValidator:
    """Validates BeeScript workflows for correctness and feasibility."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, script: BeeScript) -> bool:
        """Validate a complete BeeScript workflow."""
        self.errors.clear()
        self.warnings.clear()
        
        # Basic validation
        if not script.goal or not script.goal.strip():
            self.errors.append("Goal cannot be empty")
        
        if script.budget_credits <= 0:
            self.errors.append("Budget must be positive")
        
        if not script.subtasks:
            self.errors.append("At least one subtask is required")
        
        # Task validation
        task_ids = set()
        for task in script.subtasks:
            if not self._validate_task(task, task_ids):
                return False
            task_ids.add(task.id)
        
        # Dependency validation
        if not self._validate_dependencies(script.subtasks):
            return False
        
        # Budget validation
        if not self._validate_budget(script):
            return False
        
        return len(self.errors) == 0
    
    def _validate_task(self, task: BeeScriptTask, existing_ids: Set[str]) -> bool:
        """Validate individual task."""
        if not task.id or not task.id.strip():
            self.errors.append("Task ID cannot be empty")
            return False
        
        if task.id in existing_ids:
            self.errors.append(f"Duplicate task ID: {task.id}")
            return False
        
        if not task.agent or not task.agent.strip():
            self.errors.append(f"Task {task.id}: Agent cannot be empty")
            return False
        
        if not task.task or not task.task.strip():
            self.errors.append(f"Task {task.id}: Task type cannot be empty")
            return False
        
        if task.cost_estimate <= 0:
            self.errors.append(f"Task {task.id}: Cost estimate must be positive")
            return False
        
        if task.retry_max < 0:
            self.errors.append(f"Task {task.id}: Retry max cannot be negative")
            return False
        
        if task.timeout_seconds <= 0:
            self.errors.append(f"Task {task.id}: Timeout must be positive")
            return False
        
        return True
    
    def _validate_dependencies(self, tasks: List[BeeScriptTask]) -> bool:
        """Validate task dependencies for cycles and missing references."""
        task_ids = {task.id for task in tasks}
        
        # Check for missing dependencies
        for task in tasks:
            for dep in task.after:
                if dep not in task_ids:
                    self.errors.append(f"Task {task.id}: Unknown dependency '{dep}'")
                    return False
        
        # Check for circular dependencies using DFS
        if self._has_circular_dependencies(tasks):
            self.errors.append("Circular dependency detected in task graph")
            return False
        
        return True
    
    def _has_circular_dependencies(self, tasks: List[BeeScriptTask]) -> bool:
        """Detect circular dependencies using DFS."""
        # Build adjacency list
        graph = {task.id: task.after for task in tasks}
        
        # Track visit states: 0=unvisited, 1=visiting, 2=visited
        state = {task_id: 0 for task_id in graph}
        
        def dfs(node: str) -> bool:
            if state[node] == 1:  # Currently visiting - cycle detected
                return True
            if state[node] == 2:  # Already visited
                return False
            
            state[node] = 1  # Mark as visiting
            
            for neighbor in graph[node]:
                if dfs(neighbor):
                    return True
            
            state[node] = 2  # Mark as visited
            return False
        
        # Check each unvisited node
        for node in graph:
            if state[node] == 0 and dfs(node):
                return True
        
        return False
    
    def _validate_budget(self, script: BeeScript) -> bool:
        """Validate budget constraints."""
        total_estimated_cost = sum(task.cost_estimate for task in script.subtasks)
        
        if total_estimated_cost > script.budget_credits:
            self.errors.append(
                f"Estimated cost ({total_estimated_cost}) exceeds budget ({script.budget_credits})"
            )
            return False
        
        # Warning if budget is very tight
        if total_estimated_cost > script.budget_credits * 0.9:
            self.warnings.append("Budget is very tight - consider increasing buffer")
        
        return True


class BeeScriptExecutor:
    """Executes BeeScript workflows with dependency resolution."""
    
    def __init__(self):
        self.validator = BeeScriptValidator()
    
    def get_ready_tasks(self, script: BeeScript) -> List[BeeScriptTask]:
        """Get tasks that are ready to execute (dependencies satisfied)."""
        ready_tasks = []
        
        for task in script.subtasks:
            if task.status != TaskStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            dependencies_satisfied = True
            for dep_id in task.after:
                dep_task = self._find_task_by_id(script, dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    dependencies_satisfied = False
                    break
            
            if dependencies_satisfied:
                task.status = TaskStatus.READY
                ready_tasks.append(task)
        
        return ready_tasks
    
    def get_execution_order(self, script: BeeScript) -> List[List[str]]:
        """Get optimal execution order as list of parallel batches."""
        if not self.validator.validate(script):
            raise ValueError(f"Invalid BeeScript: {self.validator.errors}")
        
        # Topological sort with parallel batches
        batches = []
        remaining_tasks = {task.id: task for task in script.subtasks}
        
        while remaining_tasks:
            # Find tasks with no remaining dependencies
            ready_batch = []
            for task_id, task in remaining_tasks.items():
                if all(dep not in remaining_tasks for dep in task.after):
                    ready_batch.append(task_id)
            
            if not ready_batch:
                raise ValueError("Circular dependency detected")
            
            batches.append(ready_batch)
            
            # Remove completed tasks
            for task_id in ready_batch:
                del remaining_tasks[task_id]
        
        return batches
    
    def can_execute_task(self, script: BeeScript, task: BeeScriptTask) -> bool:
        """Check if a task can be executed given current state."""
        # Check budget
        if script.total_cost + task.cost_estimate > script.budget_credits:
            return False
        
        # Check retry limit
        if task.retry_count >= task.retry_max:
            return False
        
        # Check dependencies
        for dep_id in task.after:
            dep_task = self._find_task_by_id(script, dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def mark_task_completed(self, script: BeeScript, task_id: str, 
                          result: Dict[str, Any], actual_cost: int) -> None:
        """Mark a task as completed and update script state."""
        task = self._find_task_by_id(script, task_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.actual_cost = actual_cost
            script.total_cost += actual_cost
    
    def mark_task_failed(self, script: BeeScript, task_id: str, 
                        error: str, actual_cost: int = 0) -> None:
        """Mark a task as failed and update script state."""
        task = self._find_task_by_id(script, task_id)
        if task:
            task.retry_count += 1
            task.error_message = error
            task.actual_cost += actual_cost
            script.total_cost += actual_cost
            
            if task.retry_count >= task.retry_max:
                task.status = TaskStatus.FAILED
                # Mark dependent tasks as skipped
                self._mark_dependents_skipped(script, task_id)
            else:
                task.status = TaskStatus.PENDING  # Ready for retry
    
    def _find_task_by_id(self, script: BeeScript, task_id: str) -> Optional[BeeScriptTask]:
        """Find task by ID in script."""
        for task in script.subtasks:
            if task.id == task_id:
                return task
        return None
    
    def _mark_dependents_skipped(self, script: BeeScript, failed_task_id: str) -> None:
        """Mark all dependent tasks as skipped when a dependency fails."""
        def mark_skipped(task_id: str):
            for task in script.subtasks:
                if failed_task_id in task.after and task.status in [TaskStatus.PENDING, TaskStatus.READY]:
                    task.status = TaskStatus.SKIPPED
                    mark_skipped(task.id)  # Recursively skip dependents
        
        mark_skipped(failed_task_id)


def parse_beescript(data: Dict[str, Any]) -> BeeScript:
    """Parse BeeScript from dictionary/JSON data."""
    # Parse subtasks
    subtasks = []
    for task_data in data.get('subtasks', []):
        task = BeeScriptTask(
            id=task_data['id'],
            agent=task_data['agent'],
            task=task_data['task'],
            params=task_data.get('params', {}),
            after=task_data.get('after', []),
            cost_estimate=task_data.get('cost_estimate', 10),
            retry_max=task_data.get('retry_max', 2),
            timeout_seconds=task_data.get('timeout_seconds', 30)
        )
        subtasks.append(task)
    
    # Create BeeScript
    script = BeeScript(
        goal=data['goal'],
        budget_credits=data['budget_credits'],
        timeout_minutes=data.get('timeout_minutes', 10),
        subtasks=subtasks
    )
    
    return script


def beescript_to_dict(script: BeeScript) -> Dict[str, Any]:
    """Convert BeeScript to dictionary for serialization."""
    return {
        'goal': script.goal,
        'budget_credits': script.budget_credits,
        'timeout_minutes': script.timeout_minutes,
        'subtasks': [
            {
                'id': task.id,
                'agent': task.agent,
                'task': task.task,
                'params': task.params,
                'after': task.after,
                'cost_estimate': task.cost_estimate,
                'retry_max': task.retry_max,
                'timeout_seconds': task.timeout_seconds,
                'status': task.status.value,
                'actual_cost': task.actual_cost,
                'retry_count': task.retry_count,
                'error_message': task.error_message,
                'result': task.result
            }
            for task in script.subtasks
        ],
        'total_cost': script.total_cost,
        'status': script.status,
        'start_time': script.start_time,
        'end_time': script.end_time
    }