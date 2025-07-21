"""Compiler - Result aggregation."""

import json
from typing import List, Dict, Any
from pathlib import Path
from .models import WorkerResult


class Compiler:
    """Aggregates worker results into final output."""
    
    def __init__(self, results_dir: str = "results", timeout: int = 30):
        self.results_dir = Path(results_dir)
        self.timeout = timeout
        self.results_dir.mkdir(exist_ok=True)
    
    def compile_results(self, task_ids: List[str]) -> Dict[str, Any]:
        """Compile all worker results."""
        results = []
        
        if not task_ids:
            return {
                "results": results,
                "completed_tasks": 0,
                "total_tasks": 0
            }
        
        for task_id in task_ids:
            try:
                result_file = self.results_dir / f"{task_id}_result.json"
                if result_file.exists():
                    with open(result_file, 'r') as f:
                        result_data = json.load(f)
                    
                    # Validate result data before creating WorkerResult
                    if all(key in result_data for key in ['task_id', 'worker', 'outputs']):
                        results.append(WorkerResult(**result_data))
            except (json.JSONDecodeError, TypeError, ValueError, OSError) as e:
                print(f"Error reading result for task {task_id}: {e}")
                continue
        
        return {
            "results": results,
            "completed_tasks": len(results),
            "total_tasks": len(task_ids)
        }
    
    def generate_final_output(self, compiled_data: Dict[str, Any], 
                            original_prompt: str, output_path: str) -> Dict[str, Any]:
        """Generate final output file."""
        final_output = {
            "prompt": original_prompt,
            "tasks_completed": compiled_data["completed_tasks"],
            "results": [r.dict() for r in compiled_data["results"]]
        }
        
        with open(output_path, 'w') as f:
            json.dump(final_output, f, indent=2)
        
        return final_output