# Memory System

Learn how Indra's memory system enables agents to share context, learn from interactions, and maintain state across complex workflows.

## 🧠 What is the Memory System?

Indra's memory system is like a shared brain for all agents in a workflow. It allows:

- **Context sharing** between different agents and tasks
- **State persistence** across workflow executions  
- **Learning** from previous interactions
- **Data passing** between dependent tasks

Think of it as a smart notebook that all agents can read from and write to.

## 🏗️ Memory Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Queen     │    │   Router    │    │   Workers   │
│             │    │             │    │             │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                    ┌─────▼─────┐
                    │  Memory   │
                    │  Manager  │
                    └───────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
        ┌─────▼─────┐ ┌───▼───┐ ┌─────▼─────┐
        │ Session   │ │ Global│ │ Persistent│
        │ Memory    │ │Memory │ │  Storage  │
        └───────────┘ └───────┘ └───────────┘
```

## 🎯 Memory Types

### Session Memory
**Scope**: Single workflow execution  
**Lifetime**: Until workflow completes  
**Use case**: Sharing data between tasks in the same workflow

```python
# Store user preferences for this session
memory.store("user_budget", 3000, session_id="session-123")
memory.store("preferred_airline", "Delta", session_id="session-123")

# Later tasks can access this data
budget = memory.retrieve("user_budget", session_id="session-123")
airline = memory.retrieve("preferred_airline", session_id="session-123")
```

### Global Memory  
**Scope**: All workflows for a user  
**Lifetime**: Persistent across sessions  
**Use case**: User preferences, learned behaviors

```python
# Store long-term user preferences
memory.store_global("user_travel_style", "budget_conscious", user_id="user-456")
memory.store_global("dietary_restrictions", ["vegetarian"], user_id="user-456")

# Access in any future workflow
travel_style = memory.retrieve_global("user_travel_style", user_id="user-456")
```

### Persistent Storage
**Scope**: System-wide knowledge  
**Lifetime**: Permanent  
**Use case**: Facts, learned patterns, optimization data

```python
# Store system-wide knowledge
memory.store_persistent("best_flight_booking_sites", [
    "expedia.com", "kayak.com", "google.com/flights"
])

# Any agent can access this knowledge
booking_sites = memory.retrieve_persistent("best_flight_booking_sites")
```

## 🚀 Basic Usage

### Storing Information

```python
from indra.memory import MemoryManager

memory = MemoryManager()

# Simple key-value storage
memory.store("destination", "Tokyo", session_id="trip-001")

# Store complex objects
hotel_options = [
    {"name": "Hotel A", "price": 200, "rating": 4.5},
    {"name": "Hotel B", "price": 150, "rating": 4.0}
]
memory.store("hotel_options", hotel_options, session_id="trip-001")

# Store with metadata
memory.store(
    "flight_search_results", 
    flight_data,
    session_id="trip-001",
    metadata={
        "search_date": "2024-01-15",
        "search_criteria": {"destination": "Tokyo", "max_price": 800}
    }
)
```

### Retrieving Information

```python
# Simple retrieval
destination = memory.retrieve("destination", session_id="trip-001")

# Retrieve with default value
budget = memory.retrieve("budget", session_id="trip-001", default=1000)

# Retrieve with metadata
result = memory.retrieve_with_metadata("flight_search_results", session_id="trip-001")
data = result["data"]
metadata = result["metadata"]
search_date = metadata["search_date"]
```

## 🔄 Memory in Workflows

### Task-to-Task Communication

Here's how memory enables tasks to communicate:

```python
# Task 1: Research destination
def research_destination(params):
    destination = params["destination"]
    
    # Do research...
    attractions = ["Eiffel Tower", "Louvre", "Arc de Triomphe"]
    neighborhoods = ["Marais", "Saint-Germain", "Montmartre"]
    
    # Store for other tasks to use
    memory.store("attractions", attractions, session_id=params["session_id"])
    memory.store("neighborhoods", neighborhoods, session_id=params["session_id"])
    
    return {"status": "success", "attractions_found": len(attractions)}

# Task 2: Find hotels (runs after research)
def find_hotels(params):
    session_id = params["session_id"]
    
    # Use research results
    neighborhoods = memory.retrieve("neighborhoods", session_id=session_id)
    
    hotels = []
    for neighborhood in neighborhoods:
        # Search for hotels in each neighborhood
        neighborhood_hotels = search_hotels(neighborhood)
        hotels.extend(neighborhood_hotels)
    
    memory.store("hotel_options", hotels, session_id=session_id)
    return {"status": "success", "hotels_found": len(hotels)}

# Task 3: Create itinerary (runs after both previous tasks)
def create_itinerary(params):
    session_id = params["session_id"]
    
    # Use results from both previous tasks
    attractions = memory.retrieve("attractions", session_id=session_id)
    hotels = memory.retrieve("hotel_options", session_id=session_id)
    
    # Create day-by-day itinerary
    itinerary = plan_daily_activities(attractions, hotels)
    
    memory.store("final_itinerary", itinerary, session_id=session_id)
    return {"status": "success", "days_planned": len(itinerary)}
```

### Cross-Agent Memory Sharing

Different agents can share information through memory:

```python
# Travel agent stores research
class TravelWorker(BaseWorker):
    def research_destination(self, params):
        # Research and store findings
        self.memory_manager.store(
            "destination_info",
            {"climate": "temperate", "currency": "EUR", "language": "French"},
            session_id=params["session_id"]
        )

# Finance agent uses travel research  
class FinanceWorker(BaseWorker):
    def calculate_budget(self, params):
        session_id = params["session_id"]
        
        # Get destination info from travel agent
        dest_info = self.memory_manager.retrieve("destination_info", session_id=session_id)
        currency = dest_info["currency"]
        
        # Adjust budget calculations based on currency
        budget_calculation = self.calculate_for_currency(currency, params["budget"])
        
        self.memory_manager.store("budget_breakdown", budget_calculation, session_id=session_id)
```

## 🧠 Advanced Memory Features

### Memory Queries

Search and filter stored information:

```python
# Find all hotel-related data
hotel_data = memory.query(
    pattern="hotel*",  # Keys starting with "hotel"
    session_id="trip-001"
)

# Find data by metadata
recent_searches = memory.query_by_metadata(
    {"search_date": {"$gte": "2024-01-01"}},
    session_id="trip-001"
)

# Complex queries
expensive_hotels = memory.query_by_content(
    lambda data: isinstance(data, list) and 
                 any(hotel.get("price", 0) > 300 for hotel in data),
    session_id="trip-001"
)
```

### Memory Expiration

Set automatic expiration for temporary data:

```python
# Expire after 1 hour
memory.store(
    "temp_flight_prices", 
    flight_prices,
    session_id="trip-001",
    expires_in=3600  # seconds
)

# Expire at specific time
from datetime import datetime, timedelta
expire_time = datetime.now() + timedelta(hours=24)

memory.store(
    "daily_exchange_rates",
    rates,
    expires_at=expire_time
)
```

### Memory Versioning

Track changes to stored data:

```python
# Store with versioning enabled
memory.store(
    "itinerary", 
    initial_itinerary,
    session_id="trip-001",
    versioned=True
)

# Update the itinerary
memory.store(
    "itinerary",
    updated_itinerary, 
    session_id="trip-001",
    versioned=True
)

# Get version history
versions = memory.get_versions("itinerary", session_id="trip-001")
# Returns: [v1_data, v2_data]

# Get specific version
v1_itinerary = memory.retrieve("itinerary", session_id="trip-001", version=1)
```

### Memory Namespaces

Organize memory with namespaces:

```python
# Store in different namespaces
memory.store("preferences", user_prefs, namespace="user", session_id="trip-001")
memory.store("preferences", system_prefs, namespace="system", session_id="trip-001")

# Retrieve from specific namespace
user_prefs = memory.retrieve("preferences", namespace="user", session_id="trip-001")
system_prefs = memory.retrieve("preferences", namespace="system", session_id="trip-001")
```

## 🔍 Memory Patterns

### Caching Pattern

Use memory to cache expensive operations:

```python
def get_flight_prices(destination, date):
    cache_key = f"flights_{destination}_{date}"
    
    # Check cache first
    cached_prices = memory.retrieve(cache_key, expires_check=True)
    if cached_prices:
        return cached_prices
    
    # Expensive API call
    prices = expensive_flight_api_call(destination, date)
    
    # Cache for 30 minutes
    memory.store(cache_key, prices, expires_in=1800)
    
    return prices
```

### Accumulator Pattern

Build up results across multiple tasks:

```python
# Initialize accumulator
memory.store("all_recommendations", [], session_id="trip-001")

# Each task adds to it
def add_hotel_recommendations(params):
    session_id = params["session_id"]
    
    # Get current recommendations
    all_recs = memory.retrieve("all_recommendations", session_id=session_id, default=[])
    
    # Add hotel recommendations
    hotel_recs = find_hotels(params)
    all_recs.extend(hotel_recs)
    
    # Store updated list
    memory.store("all_recommendations", all_recs, session_id=session_id)

def add_restaurant_recommendations(params):
    session_id = params["session_id"]
    
    # Get current recommendations  
    all_recs = memory.retrieve("all_recommendations", session_id=session_id, default=[])
    
    # Add restaurant recommendations
    restaurant_recs = find_restaurants(params)
    all_recs.extend(restaurant_recs)
    
    # Store updated list
    memory.store("all_recommendations", all_recs, session_id=session_id)
```

### Context Passing Pattern

Pass rich context between tasks:

```python
# Task 1: Build context
def analyze_user_request(params):
    context = {
        "user_id": params["user_id"],
        "request_type": "travel_planning",
        "preferences": extract_preferences(params["request"]),
        "constraints": extract_constraints(params["request"]),
        "budget": extract_budget(params["request"])
    }
    
    memory.store("request_context", context, session_id=params["session_id"])

# Task 2: Use rich context
def find_flights(params):
    session_id = params["session_id"]
    context = memory.retrieve("request_context", session_id=session_id)
    
    # Use all context information
    preferences = context["preferences"]
    budget = context["budget"]
    constraints = context["constraints"]
    
    # Find flights that match all criteria
    flights = search_flights(
        destination=params["destination"],
        preferences=preferences,
        max_price=budget.get("flight_budget"),
        constraints=constraints
    )
```

## 🛡️ Memory Security

### Access Control

Control who can access what data:

```python
# Store with access restrictions
memory.store(
    "sensitive_data",
    user_payment_info,
    session_id="trip-001",
    access_level="private",  # Only same session can access
    allowed_agents=["finance"]  # Only finance agent can access
)

# Attempt to retrieve (will check permissions)
try:
    data = memory.retrieve("sensitive_data", session_id="trip-001", agent="travel")
except PermissionError:
    print("Travel agent cannot access payment info")
```

### Data Encryption

Encrypt sensitive data automatically:

```python
# Store encrypted data
memory.store(
    "credit_card",
    card_info,
    session_id="trip-001", 
    encrypt=True
)

# Automatically decrypted on retrieval
card_info = memory.retrieve("credit_card", session_id="trip-001")
```

## 📊 Memory Monitoring

### Usage Tracking

Monitor memory usage and performance:

```python
# Get memory statistics
stats = memory.get_stats(session_id="trip-001")
print(f"Items stored: {stats['item_count']}")
print(f"Memory used: {stats['memory_usage_mb']} MB")
print(f"Cache hit rate: {stats['cache_hit_rate']}%")

# Get most accessed items
popular_items = memory.get_popular_items(session_id="trip-001", limit=10)
```

### Memory Cleanup

Clean up old or unused data:

```python
# Clean expired items
memory.cleanup_expired()

# Clean old sessions
memory.cleanup_sessions(older_than_days=7)

# Clean by usage pattern
memory.cleanup_unused(session_id="trip-001", unused_for_hours=24)
```

## 🧪 Testing with Memory

### Memory Mocking

Mock memory for testing:

```python
import pytest
from unittest.mock import Mock

def test_hotel_search():
    # Mock memory manager
    mock_memory = Mock()
    mock_memory.retrieve.return_value = ["Paris", "Lyon", "Nice"]
    
    # Test function that uses memory
    worker = TravelWorker(client, mock_memory, credit_manager)
    result = worker.find_hotels({"session_id": "test"})
    
    # Verify memory was accessed correctly
    mock_memory.retrieve.assert_called_with("cities", session_id="test")
```

### Memory Fixtures

Create test data fixtures:

```python
@pytest.fixture
def populated_memory():
    memory = MemoryManager()
    
    # Set up test data
    memory.store("test_destination", "Tokyo", session_id="test-session")
    memory.store("test_budget", 2000, session_id="test-session")
    memory.store("test_preferences", {"style": "luxury"}, session_id="test-session")
    
    return memory

def test_itinerary_creation(populated_memory):
    worker = TravelWorker(client, populated_memory, credit_manager)
    result = worker.create_itinerary({"session_id": "test-session"})
    
    assert result["status"] == "success"
```

## 🎯 Memory Best Practices

### Naming Conventions

Use consistent, descriptive keys:

```python
# Good naming
memory.store("user_flight_preferences", prefs, session_id=session_id)
memory.store("hotel_search_results_paris", hotels, session_id=session_id)
memory.store("budget_breakdown_by_category", breakdown, session_id=session_id)

# Avoid vague names
memory.store("data", some_data, session_id=session_id)  # Too vague
memory.store("temp", temp_data, session_id=session_id)  # Not descriptive
```

### Data Structure

Store well-structured data:

```python
# Good structure
hotel_data = {
    "search_metadata": {
        "destination": "Paris",
        "check_in": "2024-06-15", 
        "check_out": "2024-06-18",
        "guests": 2
    },
    "results": [
        {
            "name": "Hotel Ritz",
            "price_per_night": 500,
            "rating": 4.8,
            "amenities": ["wifi", "spa", "restaurant"],
            "location": {"lat": 48.8566, "lng": 2.3522}
        }
    ],
    "search_stats": {
        "total_found": 25,
        "search_time_ms": 1200
    }
}
```

### Error Handling

Handle memory errors gracefully:

```python
def safe_memory_retrieve(key, session_id, default=None):
    try:
        return memory.retrieve(key, session_id=session_id)
    except KeyError:
        logger.warning(f"Memory key '{key}' not found for session {session_id}")
        return default
    except Exception as e:
        logger.error(f"Memory error retrieving '{key}': {str(e)}")
        return default
```

## 🚀 Advanced Use Cases

### Multi-User Workflows

Handle memory in multi-user scenarios:

```python
# Store user-specific data
memory.store("preferences", user1_prefs, user_id="user1", session_id="shared-trip")
memory.store("preferences", user2_prefs, user_id="user2", session_id="shared-trip")

# Merge preferences for shared decisions
def merge_user_preferences(session_id):
    all_users = memory.get_users_in_session(session_id)
    merged_prefs = {}
    
    for user_id in all_users:
        user_prefs = memory.retrieve("preferences", user_id=user_id, session_id=session_id)
        merged_prefs = merge_preferences(merged_prefs, user_prefs)
    
    memory.store("merged_preferences", merged_prefs, session_id=session_id)
```

### Learning and Adaptation

Use memory to improve over time:

```python
# Track success rates
def track_recommendation_success(recommendation_id, user_feedback):
    success_data = memory.retrieve_global("recommendation_success", default={})
    
    if recommendation_id not in success_data:
        success_data[recommendation_id] = {"total": 0, "positive": 0}
    
    success_data[recommendation_id]["total"] += 1
    if user_feedback == "positive":
        success_data[recommendation_id]["positive"] += 1
    
    memory.store_global("recommendation_success", success_data)

# Use success data to improve recommendations
def get_best_recommendations(category):
    success_data = memory.retrieve_global("recommendation_success", default={})
    
    # Sort by success rate
    sorted_recs = sorted(
        success_data.items(),
        key=lambda x: x[1]["positive"] / max(x[1]["total"], 1),
        reverse=True
    )
    
    return [rec_id for rec_id, _ in sorted_recs[:10]]
```

## 🎓 Next Steps

Now that you understand the memory system:

1. **Next**: [Credit System](credits.md) - Learn about resource management
2. **Then**: [Creating Custom Workers](../guides/custom-workers.md) - Build workers that use memory effectively
3. **After**: [Advanced BeeScript](../guides/advanced-beescript.md) - Create memory-aware workflows

## 💡 Key Takeaways

- **Memory enables collaboration** between agents and tasks
- **Three memory types** serve different scopes and lifetimes
- **Rich querying and filtering** help find the right data
- **Security features** protect sensitive information
- **Best practices** ensure maintainable and efficient memory usage

---

*Ready to learn about resource management? Check out the [Credit System](credits.md) next!*