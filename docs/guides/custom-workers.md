# Creating Custom Workers

Learn how to build your own specialized AI agents to extend Indra's capabilities.

## 🎯 What are Custom Workers?

Custom workers are specialized AI agents that handle specific types of tasks in your workflows. While Indra comes with built-in workers for travel and finance, you can create workers for any domain - from content creation to data analysis to customer support.

## 🏗️ Worker Architecture

Every Indra worker follows the same basic pattern:

```python
from indra.base_worker import BaseWorker
from indra.memory import MemoryManager
from indra.credits import CreditManager

class MyCustomWorker(BaseWorker):
    def __init__(self, client, memory_manager, credit_manager):
        super().__init__(client, memory_manager, credit_manager)
        self.name = "my_custom_worker"
        self.capabilities = ["task1", "task2", "task3"]
    
    def execute_task(self, task_type, params):
        # Your custom logic here
        pass
```

## 🚀 Quick Start: Building a Content Worker

Let's build a content creation worker step by step:

### Step 1: Create the Worker Class

```python
from indra.base_worker import BaseWorker

class ContentWorker(BaseWorker):
    def __init__(self, client, memory_manager, credit_manager):
        super().__init__(client, memory_manager, credit_manager)
        self.name = "content"
        self.capabilities = [
            "write_blog_post",
            "create_social_media",
            "generate_headlines",
            "proofread_content"
        ]
```

### Step 2: Implement Task Methods

```python
def execute_task(self, task_type, params):
    """Route tasks to specific methods"""
    if task_type == "write_blog_post":
        return self.write_blog_post(params)
    elif task_type == "create_social_media":
        return self.create_social_media(params)
    elif task_type == "generate_headlines":
        return self.generate_headlines(params)
    elif task_type == "proofread_content":
        return self.proofread_content(params)
    else:
        raise ValueError(f"Unknown task type: {task_type}")

def write_blog_post(self, params):
    """Write a blog post on a given topic"""
    topic = params.get("topic")
    word_count = params.get("word_count", 1000)
    tone = params.get("tone", "professional")
    
    # Charge credits for this operation
    self.credit_manager.charge_credits(
        params.get("session_id"), 
        30, 
        f"write_blog_post_{topic}"
    )
    
    prompt = f"""
    Write a {word_count}-word blog post about {topic}.
    Tone: {tone}
    
    Include:
    - Engaging introduction
    - 3-4 main sections with headers
    - Practical examples
    - Strong conclusion
    """
    
    response = self.client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    
    content = response.choices[0].message.content
    
    # Store in memory for other tasks to use
    self.memory_manager.store(
        f"blog_post_{topic}", 
        content,
        session_id=params.get("session_id")
    )
    
    return {
        "status": "success",
        "content": content,
        "word_count": len(content.split()),
        "topic": topic
    }
```

### Step 3: Register Your Worker

```python
# In your main application
from indra import Router
from my_workers import ContentWorker

router = Router()
content_worker = ContentWorker(client, memory_manager, credit_manager)
router.register_worker("content", content_worker)
```

## 🧠 Advanced Features

### Using Memory Effectively

Workers can store and retrieve information across tasks:

```python
def generate_headlines(self, params):
    topic = params.get("topic")
    session_id = params.get("session_id")
    
    # Check if we have existing content about this topic
    existing_content = self.memory_manager.retrieve(
        f"blog_post_{topic}", 
        session_id
    )
    
    if existing_content:
        prompt = f"Generate 5 catchy headlines for this blog post:\n{existing_content[:500]}..."
    else:
        prompt = f"Generate 5 catchy headlines about {topic}"
    
    # ... rest of implementation
```

### Error Handling

Always implement robust error handling:

```python
def execute_task(self, task_type, params):
    try:
        # Your task logic here
        result = self.perform_task(params)
        return {"status": "success", "data": result}
    
    except Exception as e:
        self.logger.error(f"Task {task_type} failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "task_type": task_type
        }
```

### Credit Management

Track and manage resource usage:

```python
def expensive_task(self, params):
    session_id = params.get("session_id")
    
    # Check if user has enough credits
    balance = self.credit_manager.get_balance(session_id)
    if balance < 50:
        return {
            "status": "error",
            "error": "Insufficient credits for this task"
        }
    
    # Charge credits upfront
    self.credit_manager.charge_credits(session_id, 50, "expensive_task")
    
    try:
        # Perform the task
        result = self.do_expensive_work(params)
        return {"status": "success", "data": result}
    
    except Exception as e:
        # Refund credits on failure
        self.credit_manager.refund_credits(session_id, 50, "expensive_task_failed")
        raise e
```

## 📋 Worker Best Practices

### 1. Clear Capability Definition

```python
class DataAnalysisWorker(BaseWorker):
    def __init__(self, client, memory_manager, credit_manager):
        super().__init__(client, memory_manager, credit_manager)
        self.name = "data_analysis"
        self.capabilities = [
            "analyze_csv",
            "generate_charts",
            "statistical_summary",
            "trend_analysis"
        ]
        # Define what each capability does
        self.capability_descriptions = {
            "analyze_csv": "Analyze CSV data and provide insights",
            "generate_charts": "Create visualizations from data",
            "statistical_summary": "Generate statistical summaries",
            "trend_analysis": "Identify trends in time series data"
        }
```

### 2. Structured Return Values

Always return consistent, structured results:

```python
def analyze_csv(self, params):
    try:
        # Process the data
        insights = self.process_csv(params["file_path"])
        
        return {
            "status": "success",
            "task_type": "analyze_csv",
            "data": {
                "insights": insights,
                "row_count": len(insights),
                "columns": list(insights.keys())
            },
            "metadata": {
                "processing_time": 2.3,
                "credits_used": 15
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "task_type": "analyze_csv",
            "error": str(e),
            "error_type": type(e).__name__
        }
```

### 3. Logging and Observability

```python
import logging

class MyWorker(BaseWorker):
    def __init__(self, client, memory_manager, credit_manager):
        super().__init__(client, memory_manager, credit_manager)
        self.logger = logging.getLogger(f"indra.workers.{self.name}")
    
    def execute_task(self, task_type, params):
        self.logger.info(f"Starting task {task_type} with params: {params}")
        
        start_time = time.time()
        result = self.perform_task(task_type, params)
        duration = time.time() - start_time
        
        self.logger.info(f"Task {task_type} completed in {duration:.2f}s")
        return result
```

## 🔌 Integration Examples

### E-commerce Worker

```python
class EcommerceWorker(BaseWorker):
    def __init__(self, client, memory_manager, credit_manager):
        super().__init__(client, memory_manager, credit_manager)
        self.name = "ecommerce"
        self.capabilities = [
            "product_research",
            "price_comparison",
            "review_analysis",
            "inventory_check"
        ]
    
    def product_research(self, params):
        product_name = params.get("product")
        budget = params.get("budget")
        
        prompt = f"""
        Research the product "{product_name}" with a budget of ${budget}.
        
        Provide:
        1. Top 3 recommended options
        2. Price comparison
        3. Key features
        4. Customer ratings
        5. Best places to buy
        """
        
        # Implementation here...
```

### Customer Support Worker

```python
class SupportWorker(BaseWorker):
    def __init__(self, client, memory_manager, credit_manager):
        super().__init__(client, memory_manager, credit_manager)
        self.name = "support"
        self.capabilities = [
            "answer_question",
            "escalate_issue",
            "generate_ticket",
            "knowledge_search"
        ]
    
    def answer_question(self, params):
        question = params.get("question")
        customer_context = params.get("customer_context", {})
        
        # Check knowledge base first
        kb_result = self.memory_manager.retrieve(
            f"kb_search_{hash(question)}", 
            params.get("session_id")
        )
        
        if not kb_result:
            # Generate answer using AI
            prompt = f"""
            Customer question: {question}
            Customer context: {customer_context}
            
            Provide a helpful, professional response.
            """
            # Implementation here...
```

## 🧪 Testing Your Workers

Create comprehensive tests for your workers:

```python
import pytest
from unittest.mock import Mock
from my_workers import ContentWorker

class TestContentWorker:
    def setup_method(self):
        self.mock_client = Mock()
        self.mock_memory = Mock()
        self.mock_credits = Mock()
        self.worker = ContentWorker(
            self.mock_client, 
            self.mock_memory, 
            self.mock_credits
        )
    
    def test_write_blog_post(self):
        # Mock the OpenAI response
        self.mock_client.chat.completions.create.return_value.choices[0].message.content = "Test blog post content"
        
        params = {
            "topic": "AI trends",
            "word_count": 500,
            "session_id": "test-123"
        }
        
        result = self.worker.write_blog_post(params)
        
        assert result["status"] == "success"
        assert "AI trends" in result["topic"]
        assert result["content"] == "Test blog post content"
        
        # Verify credits were charged
        self.mock_credits.charge_credits.assert_called_once()
        
        # Verify content was stored in memory
        self.mock_memory.store.assert_called_once()
```

## 📚 Real-World Examples

Check out these complete worker implementations:

- **[Travel Worker](../examples/travel-worker.md)** - Flight booking and itinerary planning
- **[Finance Worker](../examples/finance-worker.md)** - Budget analysis and financial planning
- **[Research Worker](../examples/research-worker.md)** - Web research and data gathering
- **[Marketing Worker](../examples/marketing-worker.md)** - Campaign creation and analysis

## 🚀 Deployment

Once your worker is ready, deploy it:

```python
# workers/my_custom_worker.py
from indra.base_worker import BaseWorker

class MyCustomWorker(BaseWorker):
    # Your implementation here
    pass

# main.py
from indra import Queen, Router, Compiler
from workers.my_custom_worker import MyCustomWorker

# Initialize Indra
queen = Queen(client)
router = Router()
compiler = Compiler()

# Register your worker
my_worker = MyCustomWorker(client, memory_manager, credit_manager)
router.register_worker("my_custom", my_worker)

# Now you can use it in workflows
script = queen.generate_beescript(
    "Use my custom worker to process this data",
    budget_credits=100
)
```

## 🎯 Next Steps

- **Learn More**: [Advanced BeeScript](advanced-beescript.md) - Use your workers in complex workflows
- **See Examples**: [Custom Worker Examples](../examples/custom-workers.md) - Real implementations
- **Get Help**: [Troubleshooting](../troubleshooting/common-issues.md) - Common worker issues

---

*Ready to build your first worker? Start with the [Quick Start example](#quick-start-building-a-content-worker) above!*