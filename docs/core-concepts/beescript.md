# BeeScript Workflows

BeeScript is Indra's workflow definition language - a simple, powerful way to describe complex multi-step processes. Think of it as a recipe that tells Indra exactly what to do, when to do it, and how much it should cost.

## 🍯 Why "BeeScript"?

Just like bees in a hive work together with clear roles and dependencies, BeeScript workflows coordinate AI agents with specific tasks and relationships. The Queen plans, workers execute, and everything flows together naturally.

## 📝 Basic Structure

Every BeeScript workflow has four main parts:

```json
{
  "goal": "What you want to accomplish",
  "budget_credits": 100,
  "timeout_minutes": 10,
  "subtasks": [
    {
      "id": "unique_task_name",
      "agent": "which_worker_to_use",
      "task": "what_to_do",
      "params": {"key": "value"},
      "after": ["dependencies"],
      "cost_estimate": 25,
      "retry_max": 2,
      "timeout_seconds": 30
    }
  ]
}
```

Let's break down each part:

## 🎯 Workflow Properties

### `goal` (required)
A clear, one-line description of what this workflow accomplishes.

```json
"goal": "Plan a comprehensive 5-day trip to Tokyo with cultural activities"
```

**Good goals:**
- Specific and actionable
- Clear success criteria
- Focused on outcomes

**Avoid:**
- Vague descriptions ("do some stuff")
- Multiple unrelated goals
- Technical implementation details

### `budget_credits` (required)
The maximum number of credits this workflow can spend.

```json
"budget_credits": 150
```

**Credit Guidelines:**
- Simple tasks: 10-30 credits
- Complex workflows: 100-300 credits
- Start conservative and adjust based on results

### `timeout_minutes` (optional, default: 10)
Maximum time the entire workflow can run.

```json
"timeout_minutes": 15
```

### `subtasks` (required)
The list of tasks that make up your workflow.

## 🔧 Task Properties

### Core Properties

#### `id` (required)
A unique identifier for this task. Use descriptive names that indicate the task's purpose.

```json
"id": "find_tokyo_flights"
```

**Good IDs:**
- `research_destination`
- `calculate_total_budget`
- `create_final_report`

**Avoid:**
- `task1`, `task2` (not descriptive)
- `do_stuff` (too vague)
- Spaces or special characters

#### `agent` (required)
Which worker should handle this task.

```json
"agent": "travel"
```

**Available Agents:**
- `travel` - Flights, hotels, itineraries, destination research
- `finance` - Cost calculations, budgets, financial analysis
- `compiler` - Combining results, generating reports

#### `task` (required)
The specific action this agent should perform.

```json
"task": "find_flights"
```

**Travel Tasks:**
- `find_flights` - Search for flight options
- `find_hotels` - Search for accommodations
- `research_destination` - Get destination information
- `create_itinerary` - Plan daily activities
- `travel_planning` - Comprehensive travel planning

**Finance Tasks:**
- `calculate_trip_cost` - Estimate total expenses
- `budget_breakdown` - Detailed cost analysis
- `savings_plan` - Create savings strategy
- `currency_conversion` - Convert currencies

#### `params` (optional)
Parameters to pass to the agent.

```json
"params": {
  "destination": "Tokyo",
  "duration": "5 days",
  "budget_range": "mid-range"
}
```

**Common Parameters:**
- `destination` - Where to focus the task
- `duration` - How long (trip length, analysis period)
- `budget_range` - "budget", "mid-range", or "luxury"
- `total_budget` - Maximum amount to spend

### Dependency Management

#### `after` (optional)
List of task IDs that must complete before this task can start.

```json
"after": ["research_destination", "find_flights"]
```

**Dependency Examples:**
```json
{
  "id": "find_flights",
  "after": ["research_destination"]
},
{
  "id": "calculate_budget", 
  "after": ["find_flights", "find_hotels"]
},
{
  "id": "final_report",
  "after": ["calculate_budget"]
}
```

### Resource Management

#### `cost_estimate` (optional, default: 10)
Expected credit cost for this task.

```json
"cost_estimate": 25
```

**Cost Guidelines:**
- Simple lookups: 5-15 credits
- Complex analysis: 15-30 credits
- Multi-step processing: 25-50 credits

#### `retry_max` (optional, default: 2)
Maximum number of retry attempts if the task fails.

```json
"retry_max": 3
```

**Retry Guidelines:**
- Critical tasks: 3 retries
- Standard tasks: 2 retries
- Optional tasks: 1 retry

#### `timeout_seconds` (optional, default: 30)
Maximum time this individual task can run.

```json
"timeout_seconds": 45
```

## 🌟 Complete Example

Here's a real-world BeeScript for planning a comprehensive trip:

```json
{
  "goal": "Plan a 5-day cultural trip to Tokyo with budget analysis",
  "budget_credits": 200,
  "timeout_minutes": 15,
  "subtasks": [
    {
      "id": "research_tokyo",
      "agent": "travel",
      "task": "research_destination",
      "params": {
        "destination": "Tokyo",
        "duration": "5 days",
        "interests": ["culture", "food", "temples"]
      },
      "cost_estimate": 20,
      "retry_max": 2,
      "timeout_seconds": 30
    },
    {
      "id": "find_flights",
      "agent": "travel",
      "task": "find_flights",
      "params": {
        "destination": "Tokyo",
        "duration": "5 days"
      },
      "after": ["research_tokyo"],
      "cost_estimate": 30,
      "retry_max": 3,
      "timeout_seconds": 45
    },
    {
      "id": "find_hotels",
      "agent": "travel", 
      "task": "find_hotels",
      "params": {
        "destination": "Tokyo",
        "duration": "5 days",
        "budget_range": "mid-range"
      },
      "after": ["research_tokyo"],
      "cost_estimate": 25,
      "retry_max": 3,
      "timeout_seconds": 40
    },
    {
      "id": "calculate_budget",
      "agent": "finance",
      "task": "calculate_trip_cost",
      "params": {
        "destination": "Tokyo",
        "duration": "5 days",
        "total_budget": 4000
      },
      "after": ["find_flights", "find_hotels"],
      "cost_estimate": 30,
      "retry_max": 2,
      "timeout_seconds": 35
    },
    {
      "id": "create_itinerary",
      "agent": "travel",
      "task": "create_itinerary",
      "params": {
        "destination": "Tokyo",
        "duration": "5 days",
        "focus": "cultural_experiences"
      },
      "after": ["research_tokyo", "calculate_budget"],
      "cost_estimate": 40,
      "retry_max": 2,
      "timeout_seconds": 60
    },
    {
      "id": "final_report",
      "agent": "compiler",
      "task": "compile_travel_plan",
      "params": {
        "format": "comprehensive_report"
      },
      "after": ["create_itinerary"],
      "cost_estimate": 25,
      "retry_max": 1,
      "timeout_seconds": 30
    }
  ]
}
```

## 🔄 Execution Flow

This workflow will execute like this:

```
1. research_tokyo (starts immediately)
   ↓
2. find_flights & find_hotels (run in parallel after research)
   ↓
3. calculate_budget (waits for both flights and hotels)
   ↓
4. create_itinerary (waits for research and budget)
   ↓
5. final_report (waits for itinerary)
```

## 🎨 Creating BeeScript

### Method 1: Let the Queen Generate It

The easiest way is to let Indra create the BeeScript for you:

```python
from indra.queen import Queen
from openai import OpenAI

queen = Queen(OpenAI())
script = queen.generate_beescript(
    "Plan a weekend trip to Paris with a $2000 budget",
    budget_credits=150,
    timeout_minutes=10
)

print(f"Generated workflow: {script.goal}")
print(f"Tasks: {len(script.subtasks)}")
```

### Method 2: Write It Yourself

For full control, create your own BeeScript:

```python
from indra.beescript import parse_beescript

script_data = {
    "goal": "My custom workflow",
    "budget_credits": 100,
    "subtasks": [
        {
            "id": "step1",
            "agent": "travel",
            "task": "research_destination",
            "params": {"destination": "Paris"}
        }
    ]
}

script = parse_beescript(script_data)
```

### Method 3: Load from File

Save your BeeScript as JSON and load it:

```python
import json
from indra.beescript import parse_beescript

with open('my_workflow.json', 'r') as f:
    script_data = json.load(f)

script = parse_beescript(script_data)
```

## ✅ Validation Rules

Indra automatically validates your BeeScript:

### Required Fields
- Every workflow must have `goal`, `budget_credits`, and `subtasks`
- Every task must have `id`, `agent`, and `task`

### Unique IDs
- All task IDs must be unique within a workflow

### Valid Dependencies
- Tasks in `after` must reference existing task IDs
- No circular dependencies allowed

### Budget Constraints
- Total estimated cost cannot exceed `budget_credits`

### Realistic Values
- All timeouts and costs must be positive numbers
- Retry counts cannot be negative

## 🚨 Common Mistakes

### Circular Dependencies
```json
// ❌ This will fail
{
  "id": "task1",
  "after": ["task2"]
},
{
  "id": "task2", 
  "after": ["task1"]
}
```

### Missing Dependencies
```json
// ❌ This will fail - "nonexistent_task" doesn't exist
{
  "id": "my_task",
  "after": ["nonexistent_task"]
}
```

### Budget Overrun
```json
// ❌ This will fail - 150 credits needed but only 100 budgeted
{
  "budget_credits": 100,
  "subtasks": [
    {"cost_estimate": 75},
    {"cost_estimate": 75}
  ]
}
```

## 🎯 Best Practices

### 1. Start Simple
Begin with linear workflows, then add parallelism:

```json
// Good: Simple linear flow
"subtasks": [
  {"id": "step1", "agent": "travel", "task": "research"},
  {"id": "step2", "agent": "travel", "task": "find_flights", "after": ["step1"]},
  {"id": "step3", "agent": "finance", "task": "calculate_cost", "after": ["step2"]}
]
```

### 2. Use Descriptive Names
Make your workflow self-documenting:

```json
// Good: Clear, descriptive names
"id": "research_tokyo_attractions"
"id": "find_budget_flights_to_tokyo"
"id": "calculate_total_trip_cost"
```

### 3. Plan Dependencies Carefully
Think about what information each task needs:

```json
// Good: Logical dependencies
{
  "id": "find_hotels",
  "after": ["research_destination"]  // Need to know the area first
},
{
  "id": "calculate_budget",
  "after": ["find_flights", "find_hotels"]  // Need prices from both
}
```

### 4. Set Realistic Budgets
Leave room for retries and unexpected costs:

```json
// Good: 20% buffer for safety
{
  "budget_credits": 120,  // For workflow that estimates 100 credits
  "subtasks": [...]
}
```

### 5. Use Appropriate Timeouts
Match timeouts to task complexity:

```json
// Good: Timeouts match task complexity
{
  "id": "simple_lookup",
  "timeout_seconds": 15
},
{
  "id": "complex_analysis", 
  "timeout_seconds": 60
}
```

## 🔧 Advanced Features

### Conditional Execution
While not directly supported, you can create conditional workflows by using the memory system:

```python
# Task 1 stores a decision
memory.store("needs_visa", True)

# Task 2 can check and act accordingly
needs_visa = memory.retrieve("needs_visa")
if needs_visa:
    # Include visa-related tasks
```

### Dynamic Parameters
Use memory to pass information between tasks:

```python
# Task 1 finds the best price
memory.store("best_flight_price", 650)

# Task 2 uses it for budget calculation
flight_price = memory.retrieve("best_flight_price")
```

### Error Recovery
Design workflows that can handle partial failures:

```json
{
  "id": "backup_hotel_search",
  "agent": "travel",
  "task": "find_hotels",
  "params": {"budget_range": "budget"},  // Fallback to cheaper options
  "retry_max": 1
}
```

## 🎓 Next Steps

Now that you understand BeeScript, explore:

1. **[Agents and Workers](agents-workers.md)** - Learn about the components that execute your workflows
2. **[Memory System](memory.md)** - See how tasks share information
3. **[Advanced BeeScript Guide](../guides/advanced-beescript.md)** - Master complex workflows

---

*Ready to learn about the agents that execute your workflows? Check out [Agents and Workers](agents-workers.md)!*