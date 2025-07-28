# BeeScript API Reference

Complete technical reference for working with BeeScript workflows programmatically.

## 📚 Core Classes

### `BeeScript`

The main workflow container that holds all tasks and metadata.

```python
from indra.beescript import BeeScript, BeeScriptTask

script = BeeScript(
    goal="Plan a trip to Tokyo",
    budget_credits=200,
    timeout_minutes=15,
    subtasks=[...]
)
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `goal` | `str` | Human-readable description of the workflow goal |
| `budget_credits` | `int` | Maximum credits this workflow can consume |
| `timeout_minutes` | `int` | Maximum execution time in minutes (default: 10) |
| `subtasks` | `List[BeeScriptTask]` | List of tasks in the workflow |
| `total_cost` | `int` | Running total of credits spent (runtime) |
| `status` | `str` | Current workflow status (runtime) |
| `start_time` | `Optional[float]` | Workflow start timestamp (runtime) |
| `end_time` | `Optional[float]` | Workflow completion timestamp (runtime) |

#### Methods

None - `BeeScript` is a data container.

---

### `BeeScriptTask`

Individual task within a workflow.

```python
from indra.beescript import BeeScriptTask, TaskStatus

task = BeeScriptTask(
    id="find_flights",
    agent="travel",
    task="find_flights",
    params={"destination": "Tokyo"},
    after=["research_destination"],
    cost_estimate=30,
    retry_max=3,
    timeout_seconds=45
)
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Unique task identifier |
| `agent` | `str` | Worker agent to execute this task |
| `task` | `str` | Specific task type to perform |
| `params` | `Dict[str, Any]` | Parameters to pass to the agent |
| `after` | `List[str]` | Task IDs this task depends on |
| `cost_estimate` | `int` | Estimated credit cost (default: 10) |
| `retry_max` | `int` | Maximum retry attempts (default: 2) |
| `timeout_seconds` | `int` | Task timeout in seconds (default: 30) |
| `status` | `TaskStatus` | Current task status (runtime) |
| `actual_cost` | `int` | Actual credits consumed (runtime) |
| `retry_count` | `int` | Current retry attempt (runtime) |
| `error_message` | `Optional[str]` | Error details if failed (runtime) |
| `result` | `Optional[Dict[str, Any]]` | Task output if completed (runtime) |

#### Methods

None - `BeeScriptTask` is a data container.

---

### `TaskStatus`

Enumeration of possible task states.

```python
from indra.beescript import TaskStatus

# Available statuses
TaskStatus.PENDING      # Task not yet started
TaskStatus.READY        # Dependencies satisfied, ready to run
TaskStatus.IN_PROGRESS  # Currently executing
TaskStatus.COMPLETED    # Successfully finished
TaskStatus.FAILED       # Failed after all retries
TaskStatus.SKIPPED      # Skipped due to dependency failure
```

## 🔧 Utility Functions

### `parse_beescript(data: Dict[str, Any]) -> BeeScript`

Parse a BeeScript from dictionary/JSON data.

```python
from indra.beescript import parse_beescript

script_data = {
    "goal": "Plan a trip",
    "budget_credits": 100,
    "subtasks": [
        {
            "id": "research",
            "agent": "travel",
            "task": "research_destination",
            "params": {"destination": "Paris"}
        }
    ]
}

script = parse_beescript(script_data)
```

**Parameters:**
- `data` - Dictionary containing BeeScript workflow definition

**Returns:**
- `BeeScript` object

**Raises:**
- `KeyError` - If required fields are missing
- `ValueError` - If data is malformed

---

### `beescript_to_dict(script: BeeScript) -> Dict[str, Any]`

Convert a BeeScript object back to dictionary format.

```python
from indra.beescript import beescript_to_dict

script_dict = beescript_to_dict(script)

# Save to JSON file
import json
with open('workflow.json', 'w') as f:
    json.dump(script_dict, f, indent=2)
```

**Parameters:**
- `script` - BeeScript object to convert

**Returns:**
- Dictionary representation including runtime state

## ✅ Validation Classes

### `BeeScriptValidator`

Validates BeeScript workflows for correctness.

```python
from indra.beescript import BeeScriptValidator

validator = BeeScriptValidator()
is_valid = validator.validate(script)

if not is_valid:
    print("Errors:", validator.errors)
    print("Warnings:", validator.warnings)
```

#### Methods

##### `validate(script: BeeScript) -> bool`

Validate a complete BeeScript workflow.

**Parameters:**
- `script` - BeeScript to validate

**Returns:**
- `True` if valid, `False` if errors found

**Side Effects:**
- Populates `validator.errors` and `validator.warnings` lists

##### Properties

| Property | Type | Description |
|----------|------|-------------|
| `errors` | `List[str]` | List of validation errors (prevent execution) |
| `warnings` | `List[str]` | List of validation warnings (non-blocking) |

#### Validation Rules

**Required Fields:**
- Workflow must have `goal`, `budget_credits`, and `subtasks`
- Tasks must have `id`, `agent`, and `task`

**Uniqueness:**
- All task IDs must be unique within workflow

**Dependencies:**
- Tasks in `after` must reference existing task IDs
- No circular dependencies allowed

**Budget:**
- Total estimated cost cannot exceed `budget_credits`

**Values:**
- All numeric values must be positive
- Retry counts cannot be negative

---

### `BeeScriptExecutor`

Manages BeeScript execution logic and dependency resolution.

```python
from indra.beescript import BeeScriptExecutor

executor = BeeScriptExecutor()

# Get tasks ready to execute
ready_tasks = executor.get_ready_tasks(script)

# Get optimal execution order
execution_order = executor.get_execution_order(script)
```

#### Methods

##### `get_ready_tasks(script: BeeScript) -> List[BeeScriptTask]`

Get tasks that are ready to execute (dependencies satisfied).

**Parameters:**
- `script` - BeeScript workflow

**Returns:**
- List of tasks with status `READY`

##### `get_execution_order(script: BeeScript) -> List[List[str]]`

Get optimal execution order as parallel batches.

**Parameters:**
- `script` - BeeScript workflow

**Returns:**
- List of batches, where each batch contains task IDs that can run in parallel

**Example:**
```python
order = executor.get_execution_order(script)
# Result: [["task1"], ["task2", "task3"], ["task4"]]
# Means: task1 first, then task2 and task3 in parallel, then task4
```

##### `can_execute_task(script: BeeScript, task: BeeScriptTask) -> bool`

Check if a task can be executed given current state.

**Parameters:**
- `script` - BeeScript workflow
- `task` - Task to check

**Returns:**
- `True` if task can execute, `False` otherwise

**Checks:**
- Budget availability
- Retry limit not exceeded
- Dependencies satisfied

##### `mark_task_completed(script: BeeScript, task_id: str, result: Dict[str, Any], actual_cost: int) -> None`

Mark a task as completed and update workflow state.

**Parameters:**
- `script` - BeeScript workflow
- `task_id` - ID of completed task
- `result` - Task output data
- `actual_cost` - Credits consumed

##### `mark_task_failed(script: BeeScript, task_id: str, error: str, actual_cost: int = 0) -> None`

Mark a task as failed and update workflow state.

**Parameters:**
- `script` - BeeScript workflow
- `task_id` - ID of failed task
- `error` - Error message
- `actual_cost` - Credits consumed before failure

**Side Effects:**
- Increments retry count
- Marks dependent tasks as skipped if max retries exceeded

## 📝 Usage Examples

### Creating a Workflow

```python
from indra.beescript import BeeScript, BeeScriptTask, parse_beescript

# Method 1: Create objects directly
tasks = [
    BeeScriptTask(
        id="research",
        agent="travel",
        task="research_destination",
        params={"destination": "Tokyo"},
        cost_estimate=20
    ),
    BeeScriptTask(
        id="flights",
        agent="travel", 
        task="find_flights",
        params={"destination": "Tokyo"},
        after=["research"],
        cost_estimate=30
    )
]

script = BeeScript(
    goal="Plan Tokyo trip",
    budget_credits=100,
    subtasks=tasks
)

# Method 2: Parse from dictionary
script_data = {
    "goal": "Plan Tokyo trip",
    "budget_credits": 100,
    "subtasks": [
        {
            "id": "research",
            "agent": "travel",
            "task": "research_destination",
            "params": {"destination": "Tokyo"},
            "cost_estimate": 20
        }
    ]
}

script = parse_beescript(script_data)
```

### Validating a Workflow

```python
from indra.beescript import BeeScriptValidator

validator = BeeScriptValidator()

if validator.validate(script):
    print("✅ Workflow is valid")
else:
    print("❌ Validation failed:")
    for error in validator.errors:
        print(f"  - {error}")
    
    if validator.warnings:
        print("⚠️ Warnings:")
        for warning in validator.warnings:
            print(f"  - {warning}")
```

### Executing a Workflow

```python
from indra.beescript import BeeScriptExecutor

executor = BeeScriptExecutor()

# Get execution plan
execution_order = executor.get_execution_order(script)
print(f"Execution plan: {execution_order}")

# Execute in batches
for batch in execution_order:
    print(f"Executing batch: {batch}")
    
    for task_id in batch:
        task = next(t for t in script.subtasks if t.id == task_id)
        
        if executor.can_execute_task(script, task):
            # Execute task (your implementation)
            result = execute_task(task)
            executor.mark_task_completed(script, task_id, result, task.cost_estimate)
        else:
            print(f"Cannot execute {task_id} - budget or retry limit exceeded")
```

### Working with Task Dependencies

```python
# Find all tasks that depend on a specific task
def find_dependents(script: BeeScript, task_id: str) -> List[str]:
    dependents = []
    for task in script.subtasks:
        if task_id in task.after:
            dependents.append(task.id)
    return dependents

# Find all dependencies of a task (recursive)
def find_all_dependencies(script: BeeScript, task_id: str) -> Set[str]:
    task = next(t for t in script.subtasks if t.id == task_id)
    dependencies = set(task.after)
    
    for dep in task.after:
        dependencies.update(find_all_dependencies(script, dep))
    
    return dependencies
```

### Saving and Loading Workflows

```python
import json
from indra.beescript import parse_beescript, beescript_to_dict

# Save workflow to file
with open('my_workflow.json', 'w') as f:
    json.dump(beescript_to_dict(script), f, indent=2)

# Load workflow from file
with open('my_workflow.json', 'r') as f:
    script_data = json.load(f)

loaded_script = parse_beescript(script_data)
```

## 🚨 Error Handling

### Common Exceptions

```python
from indra.beescript import parse_beescript, BeeScriptValidator

try:
    script = parse_beescript(malformed_data)
except KeyError as e:
    print(f"Missing required field: {e}")
except ValueError as e:
    print(f"Invalid data: {e}")

# Validation errors don't raise exceptions
validator = BeeScriptValidator()
if not validator.validate(script):
    # Handle validation errors
    pass
```

### Best Practices

1. **Always validate** workflows before execution
2. **Check budgets** before starting expensive operations
3. **Handle partial failures** gracefully
4. **Log execution state** for debugging
5. **Use descriptive task IDs** for easier troubleshooting

---

*For more examples, see the [BeeScript Guide](../guides/advanced-beescript.md) and [Examples](../examples/).*