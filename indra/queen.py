"""Queen Agent - Enhanced task breakdown using OpenAI with BeeScript support."""

import json
import uuid
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from openai import OpenAI
from .models import Task, validate_task_json
from .beescript import BeeScript, BeeScriptTask, parse_beescript, BeeScriptValidator
from .credits import estimate_task_cost


class Queen:
    """Enhanced Queen agent with BeeScript planning capabilities."""
    
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.validator = BeeScriptValidator()
        self.logger = logging.getLogger(__name__)
        
        # Load prompt templates
        prompt_path = Path(__file__).parent / "prompts" / "queen.txt"
        with open(prompt_path, 'r') as f:
            self.prompt_template = f.read()
        
        # Load BeeScript template
        beescript_prompt_path = Path(__file__).parent / "prompts" / "beescript_queen.txt"
        if beescript_prompt_path.exists():
            with open(beescript_prompt_path, 'r') as f:
                self.beescript_template = f.read()
        else:
            # Fallback template
            self.beescript_template = self._get_default_beescript_template()
    
    def generate_tasks(self, user_prompt: str) -> List[Task]:
        """Generate simple tasks from user prompt (legacy method)."""
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Generate valid JSON task lists."},
                {"role": "user", "content": self.prompt_template.format(user_prompt=user_prompt)}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        # Parse response
        response_content = response.choices[0].message.content.strip()
        task_data = json.loads(response_content)
        
        # Create Task objects
        tasks = []
        for task_dict in task_data:
            if 'id' not in task_dict:
                task_dict['id'] = f"task-{uuid.uuid4().hex[:8]}"
            tasks.append(Task(**task_dict))
        
        return tasks
    
    def generate_beescript(self, user_prompt: str, budget_credits: int = 100, 
                          timeout_minutes: int = 10, max_retries: int = 3) -> BeeScript:
        """Generate a complete BeeScript workflow from user prompt."""
        self.logger.info(f"Generating BeeScript for: {user_prompt[:100]}...")
        
        for attempt in range(max_retries):
            try:
                # Call OpenAI API with BeeScript template
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are an expert workflow planner. Generate valid BeeScript JSON."
                        },
                        {
                            "role": "user", 
                            "content": self.beescript_template.format(
                                user_prompt=user_prompt,
                                budget_credits=budget_credits,
                                timeout_minutes=timeout_minutes
                            )
                        }
                    ],
                    temperature=0.1,
                    max_tokens=3000
                )
                
                # Parse response
                response_content = response.choices[0].message.content.strip()
                
                # Extract JSON from response (handle markdown code blocks)
                if "```json" in response_content:
                    json_start = response_content.find("```json") + 7
                    json_end = response_content.find("```", json_start)
                    response_content = response_content[json_start:json_end].strip()
                elif "```" in response_content:
                    json_start = response_content.find("```") + 3
                    json_end = response_content.find("```", json_start)
                    response_content = response_content[json_start:json_end].strip()
                
                # Parse BeeScript
                script_data = json.loads(response_content)
                script = parse_beescript(script_data)
                
                # Add cost estimates to tasks
                for task in script.subtasks:
                    if task.cost_estimate == 10:  # Default value, needs estimation
                        task.cost_estimate = estimate_task_cost(task.agent, task.task, task.params)
                
                # Validate the script
                if self.validator.validate(script):
                    self.logger.info(f"Generated valid BeeScript with {len(script.subtasks)} tasks")
                    return script
                else:
                    self.logger.warning(f"Generated invalid BeeScript (attempt {attempt + 1}): {self.validator.errors}")
                    if attempt == max_retries - 1:
                        # Try to fix common issues
                        script = self._attempt_script_repair(script)
                        if self.validator.validate(script):
                            self.logger.info("Successfully repaired BeeScript")
                            return script
                        else:
                            raise ValueError(f"Failed to generate valid BeeScript: {self.validator.errors}")
            
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON decode error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to parse BeeScript JSON: {e}")
            
            except Exception as e:
                self.logger.warning(f"Error generating BeeScript (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise
        
        raise ValueError("Failed to generate valid BeeScript after all retries")
    
    def _attempt_script_repair(self, script: BeeScript) -> BeeScript:
        """Attempt to repair common issues in generated BeeScript."""
        # Fix missing task IDs
        used_ids = set()
        for task in script.subtasks:
            if not task.id or task.id in used_ids:
                task.id = f"task-{uuid.uuid4().hex[:8]}"
            used_ids.add(task.id)
        
        # Fix invalid dependencies
        valid_ids = {task.id for task in script.subtasks}
        for task in script.subtasks:
            task.after = [dep for dep in task.after if dep in valid_ids]
        
        # Fix budget issues
        total_estimated = sum(task.cost_estimate for task in script.subtasks)
        if total_estimated > script.budget_credits:
            # Scale down cost estimates proportionally
            scale_factor = (script.budget_credits * 0.9) / total_estimated
            for task in script.subtasks:
                task.cost_estimate = max(1, int(task.cost_estimate * scale_factor))
        
        # Fix negative or zero values
        for task in script.subtasks:
            task.cost_estimate = max(1, task.cost_estimate)
            task.retry_max = max(0, task.retry_max)
            task.timeout_seconds = max(10, task.timeout_seconds)
        
        return script
    
    def _get_default_beescript_template(self) -> str:
        """Get default BeeScript generation template."""
        return """
Generate a BeeScript workflow for the following request:

USER REQUEST: {user_prompt}

CONSTRAINTS:
- Budget: {budget_credits} credits maximum
- Timeout: {timeout_minutes} minutes maximum
- Available agents: travel, finance, compiler
- Task types: find_flights, find_hotels, travel_planning, calculate_trip_cost, budget_breakdown, compile_results

AVAILABLE AGENTS AND THEIR CAPABILITIES:
- travel: find_flights, find_hotels, travel_planning, research_destination
- finance: calculate_trip_cost, budget_breakdown, savings_plan, currency_conversion
- compiler: compile_results, generate_report, create_summary

Generate a valid BeeScript JSON with the following structure:
{{
  "goal": "Clear description of the overall goal",
  "budget_credits": {budget_credits},
  "timeout_minutes": {timeout_minutes},
  "subtasks": [
    {{
      "id": "unique_task_id",
      "agent": "agent_name",
      "task": "task_type",
      "params": {{"key": "value"}},
      "after": ["dependency_task_id"],
      "cost_estimate": 15,
      "retry_max": 2,
      "timeout_seconds": 30
    }}
  ]
}}

IMPORTANT:
1. Each task must have a unique ID
2. Dependencies in "after" must reference valid task IDs
3. No circular dependencies
4. Total estimated cost should not exceed budget
5. Use realistic cost estimates (5-50 credits per task)
6. Include appropriate parameters for each task
7. Create logical task dependencies

Generate the BeeScript JSON:
"""