# Indra Documentation

Welcome to the comprehensive documentation for **Indra** - the AI agent orchestration framework that makes complex workflows simple.

## 📚 Documentation Structure

### 🚀 [Getting Started](getting-started/)
Perfect for newcomers who want to get up and running quickly.
- [Installation Guide](getting-started/installation.md)
- [Quick Start Tutorial](getting-started/quick-start.md)
- [Your First Workflow](getting-started/first-workflow.md)

### 🧠 [Core Concepts](core-concepts/)
Understand the fundamental ideas behind Indra.
- [What is Indra?](core-concepts/what-is-indra.md)
- [BeeScript Workflows](core-concepts/beescript.md)
- [Agents and Workers](core-concepts/agents-workers.md)
- [Memory System](core-concepts/memory.md)
- [Credit System](core-concepts/credits.md)

### 📖 [API Reference](api-reference/)
Detailed technical documentation for developers.
- [Queen Agent](api-reference/queen.md)
- [Router](api-reference/router.md)
- [Compiler](api-reference/compiler.md)
- [BeeScript DSL](api-reference/beescript.md)
- [Memory API](api-reference/memory.md)
- [Credits API](api-reference/credits.md)

### 💡 [Examples](examples/)
Real-world examples to learn from.
- [Travel Planning](examples/travel-planning.md)
- [Budget Analysis](examples/budget-analysis.md)
- [Complex Workflows](examples/complex-workflows.md)
- [Custom Workers](examples/custom-workers.md)

### 📋 [Guides](guides/)
Step-by-step tutorials for specific tasks.
- [Creating Custom Workers](guides/custom-workers.md)

## 🎯 What is Indra?

Indra is an AI agent orchestration framework that helps you build complex, multi-step workflows using specialized AI agents. Think of it as a conductor for an orchestra of AI agents - each agent has its specialty, and Indra coordinates them to accomplish complex tasks.

### Key Features

- **🧠 Smart Planning**: Automatically breaks down complex requests into manageable tasks
- **🔗 Dependency Management**: Handles task dependencies and parallel execution
- **💰 Budget Control**: Tracks and manages resource usage with a credit system
- **🧠 Memory**: Maintains context across tasks for better results
- **🔄 Fault Tolerance**: Automatically retries failed tasks with smart backoff
- **📊 Observability**: Complete audit trail of all operations

## 🚀 Quick Example

Here's a simple example of what Indra can do:

```python
from indra import Queen, Router, Compiler
from openai import OpenAI

# Initialize Indra
client = OpenAI(api_key="your-api-key")
queen = Queen(client)
router = Router()
compiler = Compiler()

# Create a complex workflow
script = queen.generate_beescript(
    "Plan a 5-day trip to Tokyo with a $3000 budget",
    budget_credits=200
)

# Execute the workflow
router.dispatch_tasks(script.subtasks)
completed = router.wait_for_completion([task.id for task in script.subtasks])

# Get results
results = compiler.compile_results([task.id for task in script.subtasks])
```

This simple code will:
1. Break down the request into specific tasks (flights, hotels, budget analysis)
2. Execute tasks in the right order (respecting dependencies)
3. Track costs and manage the budget
4. Compile everything into a comprehensive travel plan

## 🎓 Learning Path

**New to Indra?** Follow this learning path:

1. **Start Here**: [What is Indra?](core-concepts/what-is-indra.md)
2. **Get Running**: [Quick Start Tutorial](getting-started/quick-start.md)
3. **Learn the Basics**: [BeeScript Workflows](core-concepts/beescript.md)
4. **Try Examples**: [Travel Planning Example](examples/travel-planning.md)
5. **Go Deeper**: [Advanced BeeScript Guide](guides/advanced-beescript.md)

## 🤝 Community & Support

- **GitHub**: [Five-Research/indra-mvp](https://github.com/Five-Research/indra-mvp)
- **Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas

## 📝 Contributing

We welcome contributions! Please check our GitHub repository for issues and feature requests.

---

*Ready to get started? Head over to the [Installation Guide](getting-started/installation.md)!*