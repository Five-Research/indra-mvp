"""Queen Agent - Task breakdown using OpenAI."""

import json
import uuid
from typing import List
from pathlib import Path
from openai import OpenAI
from .models import Task, validate_task_json


class Queen:
    """Breaks down user prompts into structured tasks."""
    
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        
        # Load prompt template
        prompt_path = Path(__file__).parent / "prompts" / "queen.txt"
        with open(prompt_path, 'r') as f:
            self.prompt_template = f.read()
    
    def generate_tasks(self, user_prompt: str) -> List[Task]:
        """Generate tasks from user prompt."""
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