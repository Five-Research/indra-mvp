# What is Indra?

Indra is an AI agent orchestration framework that transforms complex, multi-step tasks into automated workflows. Think of it as a smart conductor that coordinates a team of specialized AI agents to accomplish sophisticated goals.

## 🎭 The Orchestra Analogy

Imagine you're conducting an orchestra:
- **You** give the overall direction ("Play Beethoven's 9th Symphony")
- **The conductor** (Indra) breaks this down into specific parts for each section
- **Musicians** (AI agents) each play their specialized instruments
- **The result** is a beautiful, coordinated performance

In Indra:
- **You** provide a high-level request ("Plan a trip to Tokyo")
- **The Queen** breaks this into specific tasks (find flights, hotels, calculate budget)
- **Workers** (travel agent, finance agent) handle their specialties
- **The result** is a comprehensive, coordinated solution

## 🏗️ Core Architecture

Indra follows a simple but powerful pattern:

```
Your Request → Queen → Router → Workers → Compiler → Results
```

Let's break down each component:

### 👑 Queen Agent
The **planning brain** of Indra. Takes your natural language request and creates a detailed workflow.

**What it does:**
- Analyzes your request
- Breaks it into specific, actionable tasks
- Determines task dependencies (what needs to happen first)
- Estimates costs and timeouts
- Creates a BeeScript workflow

**Example:**
```
Input: "Plan a weekend trip to Paris"
Output: 
- Task 1: Research Paris attractions
- Task 2: Find flights (depends on Task 1)
- Task 3: Find hotels (depends on Task 1)  
- Task 4: Calculate budget (depends on Tasks 2 & 3)
```

### 🚦 Router
The **traffic controller** that manages task execution.

**What it does:**
- Takes the Queen's plan and executes it
- Manages task dependencies (ensures tasks run in the right order)
- Handles parallel execution (runs independent tasks simultaneously)
- Monitors progress and handles failures
- Retries failed tasks with smart backoff

### 👷 Workers
The **specialists** that do the actual work.

**Built-in Workers:**
- **Travel Worker**: Finds flights, hotels, creates itineraries
- **Finance Worker**: Calculates costs, manages budgets, analyzes spending

**What they do:**
- Execute specific tasks in their domain
- Return structured results
- Handle errors gracefully
- Work independently but share context

### 📋 Compiler
The **assembler** that puts everything together.

**What it does:**
- Waits for all tasks to complete
- Combines results from different workers
- Creates a comprehensive final output
- Handles partial results if some tasks fail

## 🧠 Key Concepts

### BeeScript Workflows
Indra uses **BeeScript**, a simple language for describing workflows:

```json
{
  "goal": "Plan a trip to Tokyo",
  "budget_credits": 100,
  "subtasks": [
    {
      "id": "research",
      "agent": "travel",
      "task": "research_destination",
      "params": {"destination": "Tokyo"}
    },
    {
      "id": "flights", 
      "agent": "travel",
      "task": "find_flights",
      "after": ["research"]
    }
  ]
}
```

### Memory System
Indra remembers context across tasks:

```python
# Task 1 stores information
memory.store("user_budget", 3000)
memory.store("preferred_airline", "Delta")

# Task 2 can access it later
budget = memory.retrieve("user_budget")
airline = memory.retrieve("preferred_airline")
```

### Credit System
Indra tracks and manages resource usage:

```python
# Each workflow has a budget
account = credit_manager.create_account("session-123", 200)

# Tasks consume credits
credit_manager.charge_credits("session-123", 25, "find_flights")

# You can track spending
balance = credit_manager.get_balance("session-123")  # 175 remaining
```

## 🎯 Why Use Indra?

### Traditional Approach (Manual)
```python
# You have to orchestrate everything manually
openai_client = OpenAI()

# Step 1: Find flights
flight_response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Find flights to Tokyo"}]
)

# Step 2: Parse response and find hotels
# ... lots of manual parsing and error handling ...

# Step 3: Calculate budget
# ... more manual work ...

# Step 4: Combine everything
# ... even more manual work ...
```

### Indra Approach (Automated)
```python
# Indra handles all the orchestration
queen = Queen(openai_client)
router = Router()
compiler = Compiler()

# One line creates the entire workflow
script = queen.generate_beescript("Plan a trip to Tokyo", budget_credits=200)

# One line executes everything
router.dispatch_tasks(script.subtasks)
completed = router.wait_for_completion([task.id for task in script.subtasks])

# One line gets comprehensive results
results = compiler.compile_results([task.id for task in script.subtasks])
```

## 🚀 What Makes Indra Special?

### 1. **Intelligent Planning**
- Automatically breaks down complex requests
- Handles task dependencies
- Optimizes execution order

### 2. **Fault Tolerance**
- Retries failed tasks automatically
- Handles partial failures gracefully
- Provides detailed error information

### 3. **Resource Management**
- Tracks costs in real-time
- Enforces budget constraints
- Prevents runaway spending

### 4. **Memory & Context**
- Maintains context across tasks
- Shares information between agents
- Learns from previous interactions

### 5. **Observability**
- Complete audit trail of all operations
- Detailed logging and monitoring
- Easy debugging and troubleshooting

## 🎨 Real-World Examples

### Travel Planning
```
"Plan a 5-day trip to Japan for 2 people with a $4000 budget"
→ Research destinations
→ Find flights (parallel with hotels)
→ Find hotels (parallel with flights)  
→ Calculate total costs
→ Create day-by-day itinerary
→ Generate final travel plan
```

### Business Analysis
```
"Analyze our Q3 marketing spend and suggest optimizations"
→ Gather marketing data
→ Analyze spend by channel
→ Calculate ROI metrics
→ Identify optimization opportunities
→ Generate recommendations report
```

### Content Creation
```
"Create a comprehensive blog post about AI trends in 2024"
→ Research current AI trends
→ Gather statistics and data
→ Create outline structure
→ Write detailed sections
→ Review and edit content
→ Generate final blog post
```

## 🔄 The Workflow Lifecycle

1. **Planning Phase**
   - Queen analyzes your request
   - Creates BeeScript workflow
   - Validates dependencies and budget

2. **Execution Phase**
   - Router dispatches tasks
   - Workers execute in parallel where possible
   - Memory system shares context
   - Credit system tracks costs

3. **Completion Phase**
   - Compiler waits for all tasks
   - Combines results intelligently
   - Generates comprehensive output
   - Provides execution summary

## 🎓 Learning Path

Now that you understand what Indra is, here's how to dive deeper:

1. **Next**: [BeeScript Workflows](beescript.md) - Learn the workflow language
2. **Then**: [Agents and Workers](agents-workers.md) - Understand the components
3. **After**: [Memory System](memory.md) - See how context works
4. **Finally**: [Credit System](credits.md) - Master resource management

## 💡 Key Takeaways

- **Indra orchestrates AI agents** to handle complex, multi-step tasks
- **BeeScript workflows** define what needs to be done and in what order
- **The memory system** maintains context across tasks
- **The credit system** manages resources and prevents overspending
- **Everything is observable** with detailed logging and audit trails

---

*Ready to learn about workflows? Check out [BeeScript Workflows](beescript.md) next!*