# Indra MVP - AI Agent Orchestration Framework

> A simple, file-based AI agent orchestration system that demonstrates the Queen → Router → Workers → Compiler pattern.

## Quick Start

```bash
# Install
pip install -e .

# Set API key
export OPENAI_API_KEY="your-key"

# Run demo
indra run "Plan a 3-day trip to Paris with $2000 budget"
```

## How It Works

```
User Prompt → Queen → Tasks → Router → Workers → Compiler → Results
```

1. **Queen**: Breaks down prompts into tasks using OpenAI
2. **Router**: Dispatches tasks to workers via JSON files
3. **Workers**: Execute specialized tasks (travel, finance, etc.)
4. **Compiler**: Aggregates results into final output

## Architecture

```
indra/
├── queen.py          # Task breakdown
├── router.py         # Task dispatch
├── compiler.py       # Result aggregation
├── base_worker.py    # Worker base class
├── workers/
│   ├── travel.py     # Travel planning
│   └── finance.py    # Cost calculations
└── cli.py           # Command interface
```

## Usage

### CLI Commands

```bash
# Basic usage
indra run "your prompt"

# Custom output directory
indra run "your prompt" --out results/

# Check status
indra status
```

### Adding Workers

```python
from indra.base_worker import BaseWorker, register_worker

@register_worker("my_worker")
class MyWorker(BaseWorker):
    def execute(self, **inputs):
        return {"result": "processed"}
```

## Dependencies

- `openai>=1.0.0` - OpenAI API client
- `pydantic>=2.0.0` - Data validation
- `python-json-logger>=2.0.0` - Structured logging

## Testing

```bash
python test_framework.py
```

## License

Five Labs Community License - see [LICENSE](LICENSE) file.
