# Quick Start Tutorial

Welcome to Indra! In just 5 minutes, you'll learn how to create and run your first AI workflow. Let's dive in!

## 🎯 What We'll Build

We're going to create a simple workflow that plans a weekend trip. Indra will:
1. Research the destination
2. Find flights and hotels
3. Calculate the budget
4. Create a final travel plan

## 🚀 Your First Workflow

### Step 1: Basic Setup

First, make sure Indra is installed and your API key is set:

```bash
# Check if everything is working
indra status
```

You should see:
```
✅ API Key: Configured
✅ System: Ready
```

### Step 2: Run a Simple Command

Let's start with the easiest way to use Indra:

```bash
indra run "Plan a weekend trip to Paris with a $2000 budget"
```

That's it! Indra will:
- Break down your request into specific tasks
- Execute each task using specialized AI agents
- Compile everything into a comprehensive plan
- Save the results to a JSON file

### Step 3: Understanding the Output

You'll see output like this:

```
🤖 Processing: Plan a weekend trip to Paris with a $2000 budget
👑 Generated 4 tasks
🚦 Dispatched tasks
✅ Results saved to results/result.json
📋 Completed 4 tasks
```

The results file contains your complete travel plan with flights, hotels, activities, and budget breakdown.

## 🧠 Understanding What Happened

Behind the scenes, Indra created a workflow like this:

```
User Request
     ↓
   Queen Agent (breaks down the request)
     ↓
   Router (manages task execution)
     ↓
   Workers (travel & finance agents)
     ↓
   Compiler (combines results)
     ↓
   Final Plan
```

## 💻 Using Indra in Python

For more control, you can use Indra directly in Python:

```python
from indra import Queen, Router, Compiler
from openai import OpenAI

# Initialize components
client = OpenAI(api_key="your-api-key")  # or use environment variable
queen = Queen(client)
router = Router()
compiler = Compiler()

# Create a workflow
prompt = "Plan a 3-day trip to Tokyo with a $3000 budget"

# Step 1: Generate tasks
tasks = queen.generate_tasks(prompt)
print(f"Generated {len(tasks)} tasks")

# Step 2: Execute tasks
task_ids = [task.id for task in tasks]
router.dispatch_tasks(tasks)
completed = router.wait_for_completion(task_ids)

# Step 3: Get results
if completed:
    results = compiler.compile_results(task_ids)
    final_output = compiler.generate_final_output(results, prompt, "my_trip.json")
    print(f"Trip plan saved! Completed {final_output['tasks_completed']} tasks")
```

## 🎨 Advanced: BeeScript Workflows

For complex workflows, you can use BeeScript (Indra's workflow language):

```python
from indra.queen import Queen
from openai import OpenAI

client = OpenAI()
queen = Queen(client)

# Generate a sophisticated workflow
script = queen.generate_beescript(
    "Plan a comprehensive 5-day trip to Tokyo with cultural activities",
    budget_credits=200,  # Credit budget for the workflow
    timeout_minutes=15   # Maximum time allowed
)

print(f"Created workflow: {script.goal}")
print(f"Tasks: {len(script.subtasks)}")
print(f"Budget: {script.budget_credits} credits")

# The script includes task dependencies, cost estimates, and retry logic
for task in script.subtasks:
    print(f"- {task.id}: {task.task} (cost: {task.cost_estimate} credits)")
    if task.after:
        print(f"  Depends on: {', '.join(task.after)}")
```

## 🔍 Exploring Results

Let's look at what Indra creates for you:

```python
import json

# Load your results
with open('results/result.json', 'r') as f:
    results = json.load(f)

print("Your trip plan includes:")
print(f"- Prompt: {results['prompt']}")
print(f"- Tasks completed: {results['tasks_completed']}")

# Each result contains detailed information
for result in results['results']:
    print(f"\n{result['worker']} agent found:")
    if 'flights' in result['outputs']:
        flights = result['outputs']['flights']
        print(f"  - {len(flights)} flight options")
    if 'hotels' in result['outputs']:
        hotels = result['outputs']['hotels']
        print(f"  - {len(hotels)} hotel options")
    if 'estimated_cost' in result['outputs']:
        cost = result['outputs']['estimated_cost']
        print(f"  - Estimated cost: ${cost}")
```

## 🎯 What's Next?

Now that you've run your first workflow, here are some things to try:

### Experiment with Different Requests
```bash
indra run "Find the cheapest flights to London next month"
indra run "Plan a business trip to San Francisco with meetings"
indra run "Create a budget for a family vacation to Disney World"
```

### Try Different Output Directories
```bash
indra run "Plan a ski trip to Colorado" --out ski_trip_results/
```

### Explore the Memory System
```python
from indra.memory import get_workflow_memory

# Workflows can remember context across tasks
memory = get_workflow_memory("my-session")
memory.store("preferred_airline", "Delta")
memory.store("budget_limit", 2500)

# Later tasks can access this information
airline = memory.retrieve("preferred_airline")
```

### Use the Credit System
```python
from indra.credits import get_credit_manager

# Track and manage workflow costs
credit_manager = get_credit_manager()
account = credit_manager.create_account("my-session", 100)

# Check spending
summary = credit_manager.get_account_summary("my-session")
print(f"Spent: {summary['total_spent']} credits")
print(f"Remaining: {summary['current_balance']} credits")
```

## 🚨 Common First-Time Issues

**"No results generated"**
- Check your internet connection
- Verify your OpenAI API key is valid
- Make sure you have API credits available

**"Tasks timed out"**
- Try a simpler request first
- Increase timeout: `indra run "your request" --timeout 60`

**"Permission errors"**
- Make sure you have write permissions in the current directory
- Try specifying a different output directory: `--out ~/indra_results/`

## 🎓 Learning More

Ready to dive deeper? Check out:

1. **[Core Concepts](../core-concepts/what-is-indra.md)** - Understand how Indra works
2. **[BeeScript Guide](../core-concepts/beescript.md)** - Learn the workflow language
3. **[Examples](../examples/)** - See real-world use cases
4. **[API Reference](../api-reference/)** - Detailed technical docs

## 💡 Pro Tips

- **Start simple**: Begin with basic requests and gradually make them more complex
- **Check the logs**: Look in the `logs/` directory for detailed execution information
- **Use descriptive prompts**: The more specific you are, the better results you'll get
- **Experiment with budgets**: Try different credit limits to see how it affects planning

---

*Congratulations! You've successfully run your first Indra workflow. Ready to learn more? Check out [What is Indra?](../core-concepts/what-is-indra.md)*