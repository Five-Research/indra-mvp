# Indra MVP - AI Agent Orchestration Framework

> *An intelligent AI agent orchestration system that transforms complex workflows into automated, dependency-aware task execution with enterprise-grade features.*

Indra demonstrates the **Queen → Router → Workers → Compiler** pattern with advanced capabilities including BeeScript DSL, persistent memory, credit management, and sophisticated retry logic.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -e .

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Run a complex workflow
indra run "Plan a comprehensive 5-day trip to Tokyo with cultural activities and a $4000 budget"

# Check system status
indra status
```

## 🏗️ Architecture Overview

```
User Prompt → Queen → BeeScript → Router → Workers → Compiler → Results
     ↓           ↓        ↓         ↓        ↓         ↓         ↓
  Natural    Task      Workflow   Task    Specialized  Result    Final
  Language   Planning  Definition Dispatch Execution  Aggregation Output
```

### Core Components

1. **👑 Queen Agent**: Intelligent workflow planner that converts natural language into structured BeeScript workflows with dependencies and cost estimates
2. **🚦 Router**: Dependency-aware task dispatcher with parallel execution, retry logic, and circuit breaker patterns
3. **👷 Workers**: Specialized AI agents (Travel, Finance) with memory access and domain expertise
4. **📋 Compiler**: Result aggregator that combines outputs with comprehensive audit trails

## ✨ Advanced Features

### 🧠 BeeScript DSL
Hierarchical workflow definition language with sophisticated capabilities:

```json
{
  "goal": "Plan comprehensive Tokyo trip",
  "budget_credits": 200,
  "timeout_minutes": 15,
  "subtasks": [
    {
      "id": "research_tokyo",
      "agent": "travel",
      "task": "research_destination",
      "params": {"destination": "Tokyo", "duration": "5 days"},
      "cost_estimate": 25,
      "retry_max": 2,
      "timeout_seconds": 30
    },
    {
      "id": "find_flights",
      "agent": "travel",
      "task": "find_flights",
      "after": ["research_tokyo"],
      "cost_estimate": 35,
      "retry_max": 3
    }
  ]
}
```

### 🧠 Memory System
Persistent context storage across task execution:

```python
from indra.memory import get_workflow_memory

# Store context that persists across tasks
memory = get_workflow_memory("session-123")
memory.store("user_preferences", {"airline": "Delta", "hotel_class": "4-star"})
memory.store("budget_constraints", {"max_flight": 800, "max_hotel": 200})

# Later tasks can access this context
preferences = memory.retrieve("user_preferences")
constraints = memory.retrieve("budget_constraints")
```

### 💰 Credit System
Enterprise-grade budget tracking and enforcement:

```python
from indra.credits import get_credit_manager

# Create account with budget
credit_manager = get_credit_manager()
account = credit_manager.create_account("workflow-456", 150)

# Track spending in real-time
credit_manager.charge_credits("workflow-456", 25, "flight_search")
balance = credit_manager.get_balance("workflow-456")  # 125 remaining

# Get detailed analytics
summary = credit_manager.get_account_summary("workflow-456")
spending_by_agent = credit_manager.get_spending_by_agent("workflow-456")
```

### 🔄 Intelligent Retry Logic
Exponential backoff with jitter for robust error handling:

- **Configurable retry limits** per task type
- **Exponential backoff** with randomized jitter
- **Circuit breaker patterns** to prevent cascade failures
- **Detailed error tracking** and reporting

### 📊 Comprehensive Observability
Complete audit trail and monitoring:

- **Transaction logging** for every operation
- **Execution time tracking** per task
- **Memory usage analytics** 
- **Credit consumption reports**
- **Dependency graph visualization**

## 🎯 Real-World Use Cases

### Travel Planning
```bash
indra run "Plan a 2-week European tour visiting Paris, Rome, and Barcelona with a $5000 budget including flights, hotels, and activities"
```

### Business Analysis
```bash
indra run "Analyze our Q4 marketing spend across all channels and provide optimization recommendations"
```

### Content Creation
```bash
indra run "Create a comprehensive blog post about AI trends in 2024 with statistics, examples, and expert quotes"
```

## 🛠️ Usage Examples

### Command Line Interface

```bash
# Basic workflow execution
indra run "your complex prompt here"

# Custom output directory
indra run "your prompt" --out custom_results/

# System status and health check
indra status
```

### Python API

```python
from indra import Queen, Router, Compiler
from indra.memory import get_workflow_memory
from indra.credits import get_credit_manager
from openai import OpenAI

# Initialize components
client = OpenAI()
queen = Queen(client)
router = Router()
compiler = Compiler()

# Set up session context
memory = get_workflow_memory("my-session")
credit_manager = get_credit_manager()
account = credit_manager.create_account("my-session", 200)

# Generate sophisticated workflow
script = queen.generate_beescript(
    "Plan a comprehensive business trip to San Francisco",
    budget_credits=150,
    timeout_minutes=20
)

# Execute with dependency management
router.dispatch_tasks(script.subtasks)
completed = router.wait_for_completion([task.id for task in script.subtasks])

# Compile results with audit trail
results = compiler.compile_results([task.id for task in script.subtasks])
final_output = compiler.generate_final_output(results, script.goal, "trip_plan.json")
```

### Adding Custom Workers

```python
from indra.base_worker import BaseWorker, register_worker

@register_worker("research")
class ResearchWorker(BaseWorker):
    def execute(self, **inputs):
        topic = inputs.get("topic", "")
        depth = inputs.get("depth", "basic")
        
        # Your custom research logic here
        research_data = self.conduct_research(topic, depth)
        
        return {
            "topic": topic,
            "findings": research_data,
            "sources": self.get_sources(),
            "confidence": self.calculate_confidence()
        }
```

## 🧪 Testing & Quality

```bash
# Run framework tests
python test_framework.py

# Run comprehensive integration tests
python integration_test.py

# Interactive demo launcher
python examples/launch_demo.py

# Simple trip planning demo
python examples/trip_demo.py
```

## 📚 Documentation

- **[Getting Started Guide](docs/getting-started/)** - Installation and first steps
- **[Core Concepts](docs/core-concepts/)** - Understanding Indra's architecture
- **[API Reference](docs/api-reference/)** - Detailed technical documentation
- **[Examples](docs/examples/)** - Real-world usage examples
- **[Guides](docs/guides/)** - Step-by-step tutorials

## 🏢 Enterprise Features

- **🔒 Secure Execution** - Isolated task execution with proper error boundaries
- **📈 Scalable Architecture** - Designed for high-throughput workflows
- **🔍 Full Observability** - Complete audit trails and monitoring
- **💼 Budget Management** - Enterprise-grade cost tracking and limits
- **🔄 Fault Tolerance** - Sophisticated retry and recovery mechanisms
- **🧠 Context Persistence** - Long-term memory across workflow sessions

## 🤝 Contributing

We welcome contributions! Please check our GitHub repository for issues and feature requests.

## 📄 License

**Five Labs Community License v1.0** - see [LICENSE](LICENSE) file.

This software is free for non-commercial use. For commercial licensing, contact: mehul@fivelabs.co

---

*Ready to orchestrate your AI workflows? Get started with the [Installation Guide](docs/getting-started/installation.md)!*