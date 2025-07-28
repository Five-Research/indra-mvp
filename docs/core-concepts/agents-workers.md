# Agents and Workers

Understanding the different types of AI agents in Indra and how they work together to accomplish complex tasks.

## 🎭 The Agent Ecosystem

Indra uses a multi-agent architecture where different AI agents have specialized roles:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Queen    │───▶│   Router    │───▶│   Workers   │
│  (Planner)  │    │ (Executor)  │    │(Specialists)│
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
   Creates plan       Manages tasks      Execute work
```

Each agent type has a specific responsibility and works together to create a powerful orchestration system.

## 👑 Queen Agent: The Strategic Planner

The Queen is Indra's **planning brain** - it takes your natural language requests and creates detailed, executable workflows.

### What the Queen Does

**Input Processing:**
- Analyzes natural language requests
- Identifies the core goal and requirements
- Determines complexity and scope

**Task Decomposition:**
- Breaks complex requests into specific, actionable tasks
- Identifies which worker should handle each task
- Determines task dependencies and execution order

**Resource Planning:**
- Estimates credit costs for each task
- Sets appropriate timeouts
- Plans for error handling and retries

### Queen in Action

```python
from indra import Queen

queen = Queen(openai_client)

# Simple request
script = queen.generate_beescript(
    "Find the best flight to Tokyo under $800",
    budget_credits=50
)

# Complex request  
script = queen.generate_beescript(
    "Plan a 7-day trip to Japan for 2 people with a $5000 budget, "
    "including flights, hotels, activities, and a detailed itinerary",
    budget_credits=200
)
```

**Simple Request Output:**
```json
{
  "goal": "Find the best flight to Tokyo under $800",
  "budget_credits": 50,
  "subtasks": [
    {
      "id": "flight_search",
      "agent": "travel",
      "task": "find_flights",
      "params": {
        "destination": "Tokyo",
        "max_price": 800,
        "sort_by": "price"
      },
      "estimated_credits": 25,
      "timeout": 60
    }
  ]
}
```

**Complex Request Output:**
```json
{
  "goal": "Plan a 7-day trip to Japan for 2 people with a $5000 budget",
  "budget_credits": 200,
  "subtasks": [
    {
      "id": "research_japan",
      "agent": "travel", 
      "task": "research_destination",
      "params": {"destination": "Japan", "duration": 7}
    },
    {
      "id": "find_flights",
      "agent": "travel",
      "task": "find_flights", 
      "after": ["research_japan"],
      "params": {"destination": "Japan", "passengers": 2}
    },
    {
      "id": "find_hotels",
      "agent": "travel",
      "task": "find_hotels",
      "after": ["research_japan"],
      "params": {"destination": "Japan", "nights": 7, "guests": 2}
    },
    {
      "id": "calculate_budget",
      "agent": "finance",
      "task": "analyze_costs",
      "after": ["find_flights", "find_hotels"],
      "params": {"total_budget": 5000}
    },
    {
      "id": "create_itinerary",
      "agent": "travel",
      "task": "create_itinerary",
      "after": ["calculate_budget"],
      "params": {"duration": 7, "budget_remaining": "from_budget_task"}
    }
  ]
}
```

### Queen Intelligence Features

**Dependency Detection:**
```python
# The Queen automatically figures out that:
# - Hotels and flights can be searched in parallel
# - Budget calculation needs both flight and hotel prices
# - Itinerary creation needs the budget analysis
```

**Error Anticipation:**
```python
# The Queen adds error handling:
{
  "id": "backup_hotels",
  "agent": "travel", 
  "task": "find_hotels",
  "trigger": "if_task_fails:find_hotels",
  "params": {"destination": "Japan", "budget_increase": 0.2}
}
```

## 🚦 Router: The Execution Engine

The Router takes the Queen's plan and makes it happen, managing the complex orchestration of multiple tasks.

### What the Router Does

**Task Management:**
- Receives BeeScript workflows from the Queen
- Manages task queues and execution order
- Handles parallel execution where possible

**Dependency Resolution:**
- Ensures tasks run in the correct order
- Waits for dependencies before starting tasks
- Passes results between dependent tasks

**Error Handling:**
- Retries failed tasks with exponential backoff
- Handles partial failures gracefully
- Provides detailed error reporting

### Router in Action

```python
from indra import Router

router = Router()

# Dispatch all tasks from the Queen's plan
router.dispatch_tasks(script.subtasks)

# Monitor progress
status = router.get_status()
print(f"Running: {status['running']}, Completed: {status['completed']}")

# Wait for completion
completed_tasks = router.wait_for_completion(
    [task.id for task in script.subtasks],
    timeout=300
)
```

### Router Intelligence Features

**Parallel Execution:**
```python
# These tasks run simultaneously:
# ┌─────────────┐  ┌─────────────┐
# │find_flights │  │ find_hotels │
# └─────────────┘  └─────────────┘
#        │                │
#        └────────┬───────┘
#                 ▼
#        ┌─────────────────┐
#        │ calculate_budget│
#        └─────────────────┘
```

**Smart Retries:**
```python
# Automatic retry logic:
# Attempt 1: Immediate retry
# Attempt 2: Wait 2 seconds
# Attempt 3: Wait 4 seconds  
# Attempt 4: Wait 8 seconds
# After 4 failures: Mark as failed
```

**Resource Management:**
```python
# Router tracks:
# - Credits used per task
# - Execution time per task  
# - Memory usage per task
# - Success/failure rates
```

## 👷 Workers: The Specialists

Workers are specialized AI agents that handle specific types of tasks. Each worker is an expert in their domain.

### Built-in Workers

**Travel Worker:**
```python
class TravelWorker(BaseWorker):
    capabilities = [
        "research_destination",
        "find_flights", 
        "find_hotels",
        "create_itinerary",
        "find_activities"
    ]
```

**Finance Worker:**
```python
class FinanceWorker(BaseWorker):
    capabilities = [
        "analyze_costs",
        "create_budget", 
        "track_expenses",
        "optimize_spending",
        "generate_reports"
    ]
```

### How Workers Operate

**Task Execution:**
```python
# Worker receives a task
task = {
    "id": "find_flights",
    "agent": "travel", 
    "task": "find_flights",
    "params": {
        "destination": "Tokyo",
        "departure_date": "2024-06-15",
        "max_price": 800
    }
}

# Worker processes it
result = travel_worker.execute_task("find_flights", task.params)

# Worker returns structured result
{
    "status": "success",
    "data": {
        "flights": [
            {
                "airline": "Delta",
                "price": 750,
                "departure": "2024-06-15T10:30:00",
                "arrival": "2024-06-16T14:45:00"
            }
        ]
    },
    "credits_used": 25,
    "execution_time": 12.3
}
```

**Memory Integration:**
```python
# Workers can store information for other tasks
travel_worker.memory_manager.store(
    "user_preferences", 
    {"preferred_airline": "Delta", "seat_preference": "aisle"},
    session_id="user-123"
)

# And retrieve it later
preferences = travel_worker.memory_manager.retrieve(
    "user_preferences",
    session_id="user-123" 
)
```

**Credit Management:**
```python
# Workers track their resource usage
travel_worker.credit_manager.charge_credits(
    session_id="user-123",
    credits=25,
    description="find_flights_tokyo"
)
```

## 🔄 Agent Collaboration

Here's how agents work together in a real workflow:

### Example: Trip Planning

**1. Queen Plans:**
```
User: "Plan a weekend trip to Paris"

Queen thinks:
- Need to research Paris attractions
- Need to find flights  
- Need to find hotels
- Need to calculate total cost
- Need to create itinerary

Queen creates BeeScript with 5 tasks
```

**2. Router Executes:**
```
Router receives 5 tasks:
- Starts "research_paris" immediately
- Waits for research to complete
- Starts "find_flights" and "find_hotels" in parallel
- Waits for both to complete
- Starts "calculate_cost" 
- Finally starts "create_itinerary"
```

**3. Workers Deliver:**
```
Travel Worker:
- Researches Paris attractions and neighborhoods
- Finds 3 flight options
- Finds 5 hotel options  
- Creates detailed 2-day itinerary

Finance Worker:
- Calculates total trip cost
- Breaks down costs by category
- Suggests budget optimizations
```

**4. Results Compiled:**
```
Final output includes:
- Complete Paris travel guide
- Flight and hotel recommendations
- Detailed budget breakdown
- Day-by-day itinerary
- Total cost estimate
```

## 🧠 Agent Intelligence

### Context Sharing

Agents share information through the memory system:

```python
# Travel worker stores research
memory.store("paris_attractions", [
    "Eiffel Tower", "Louvre", "Notre Dame"
])

# Later, the same worker retrieves it for itinerary
attractions = memory.retrieve("paris_attractions")
```

### Learning from Failures

```python
# If a task fails, agents learn:
if flight_search_failed:
    memory.store("flight_search_issues", {
        "error": "No flights under $500",
        "suggestion": "Increase budget or change dates"
    })
    
    # Queen can use this for future planning
    queen.adjust_strategy(memory.retrieve("flight_search_issues"))
```

### Adaptive Behavior

```python
# Agents adapt based on results:
if hotel_budget_exceeded:
    # Finance worker suggests alternatives
    finance_worker.suggest_alternatives({
        "reduce_hotel_nights": 1,
        "consider_airbnb": True,
        "look_outside_city_center": True
    })
```

## 🎯 Agent Best Practices

### For Queen Usage

```python
# Be specific in your requests
queen.generate_beescript(
    "Find a 4-star hotel in downtown Tokyo for 3 nights, "
    "check-in June 15th, budget $200/night",
    budget_credits=50
)

# Rather than vague requests
queen.generate_beescript("Find a hotel in Tokyo", budget_credits=50)
```

### For Router Management

```python
# Monitor progress
while not router.all_tasks_complete():
    status = router.get_status()
    print(f"Progress: {status['completed']}/{status['total']}")
    time.sleep(5)

# Handle failures gracefully
failed_tasks = router.get_failed_tasks()
if failed_tasks:
    print(f"Failed tasks: {[task.id for task in failed_tasks]}")
```

### For Worker Development

```python
# Always return structured results
def execute_task(self, task_type, params):
    try:
        result = self.do_work(params)
        return {
            "status": "success",
            "data": result,
            "credits_used": self.credits_used,
            "execution_time": self.execution_time
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "error_type": type(e).__name__
        }
```

## 🚀 Advanced Agent Patterns

### Multi-Stage Workflows

```python
# Complex workflows with multiple stages
script = queen.generate_beescript(
    "Research the top 5 AI companies, analyze their financials, "
    "and create an investment recommendation report",
    budget_credits=300
)

# This creates a workflow like:
# Stage 1: Research (parallel for each company)
# Stage 2: Financial analysis (depends on research)  
# Stage 3: Comparison and ranking
# Stage 4: Report generation
```

### Conditional Execution

```python
# Tasks that run based on conditions
{
    "id": "book_premium_hotel",
    "agent": "travel",
    "task": "find_hotels", 
    "condition": "if budget_remaining > 1000",
    "params": {"category": "luxury"}
}
```

### Dynamic Task Generation

```python
# Queen can create new tasks based on results
if research_reveals_multiple_cities:
    queen.add_tasks([
        create_task_for_city(city) 
        for city in discovered_cities
    ])
```

## 🎓 Learning Path

Now that you understand agents and workers:

1. **Next**: [Memory System](memory.md) - How agents share information
2. **Then**: [Credit System](credits.md) - How resource usage is managed  
3. **After**: [Creating Custom Workers](../guides/custom-workers.md) - Build your own specialists

## 💡 Key Takeaways

- **Queen** plans and strategizes, breaking down complex requests
- **Router** executes and orchestrates, managing dependencies and failures
- **Workers** specialize and deliver, handling specific types of tasks
- **All agents collaborate** through shared memory and structured communication
- **The system is extensible** - you can add your own custom workers

---

*Ready to learn how agents share information? Check out the [Memory System](memory.md) next!*