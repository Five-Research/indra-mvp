# Travel Planning Example

This comprehensive example shows how to use Indra to plan a complete trip, from initial research to final itinerary. We'll build a sophisticated workflow that handles flights, hotels, budget analysis, and activity planning.

## 🎯 What We'll Build

A complete travel planning system that:
- Researches the destination
- Finds flights and hotels in parallel
- Calculates comprehensive budget
- Creates a day-by-day itinerary
- Generates a final travel report

## 🚀 Quick Start

### Simple Travel Planning

Let's start with the easiest approach:

```python
from indra import Queen, Router, Compiler
from openai import OpenAI

# Initialize Indra
client = OpenAI()  # Uses OPENAI_API_KEY environment variable
queen = Queen(client)
router = Router()
compiler = Compiler()

# Create and execute workflow
script = queen.generate_beescript(
    "Plan a 5-day trip to Tokyo for 2 people with a $4000 budget",
    budget_credits=200,
    timeout_minutes=15
)

# Execute the workflow
task_ids = [task.id for task in script.subtasks]
router.dispatch_tasks(script.subtasks)
completed = router.wait_for_completion(task_ids)

# Get comprehensive results
if completed:
    results = compiler.compile_results(task_ids)
    final_output = compiler.generate_final_output(results, script.goal, "tokyo_trip.json")
    print(f"✅ Trip planned! Generated {final_output['tasks_completed']} recommendations")
else:
    print("⚠️ Some tasks didn't complete - check partial results")
```

### Command Line Version

Even simpler - use the command line:

```bash
indra run "Plan a romantic weekend in Paris with a $2500 budget" --out paris_trip/
```

## 🧠 Advanced: Custom BeeScript

For full control, let's create a detailed BeeScript workflow:

```python
from indra.beescript import parse_beescript
from indra.queen import Queen
from indra.router import Router
from indra.compiler import Compiler
from indra.memory import get_workflow_memory
from indra.credits import get_credit_manager
from openai import OpenAI

# Define our comprehensive travel workflow
travel_workflow = {
    "goal": "Plan a comprehensive 7-day cultural trip to Japan for 2 people",
    "budget_credits": 300,
    "timeout_minutes": 20,
    "subtasks": [
        {
            "id": "research_japan",
            "agent": "travel",
            "task": "research_destination",
            "params": {
                "destination": "Japan",
                "duration": "7 days",
                "travelers": 2,
                "interests": ["culture", "food", "temples", "gardens"],
                "season": "spring"
            },
            "cost_estimate": 25,
            "retry_max": 2,
            "timeout_seconds": 45
        },
        {
            "id": "find_international_flights",
            "agent": "travel",
            "task": "find_flights",
            "params": {
                "destination": "Tokyo",
                "duration": "7 days",
                "travelers": 2,
                "class_preference": "economy",
                "flexibility": "3_days"
            },
            "after": ["research_japan"],
            "cost_estimate": 35,
            "retry_max": 3,
            "timeout_seconds": 60
        },
        {
            "id": "find_accommodations",
            "agent": "travel",
            "task": "find_hotels",
            "params": {
                "destination": "Tokyo",
                "duration": "7 days",
                "travelers": 2,
                "budget_range": "mid-range",
                "preferences": ["central_location", "traditional_style"]
            },
            "after": ["research_japan"],
            "cost_estimate": 30,
            "retry_max": 3,
            "timeout_seconds": 50
        },
        {
            "id": "research_activities",
            "agent": "travel",
            "task": "research_activities",
            "params": {
                "destination": "Japan",
                "duration": "7 days",
                "interests": ["temples", "gardens", "food_tours", "cultural_sites"],
                "budget_per_day": 150
            },
            "after": ["research_japan"],
            "cost_estimate": 30,
            "retry_max": 2,
            "timeout_seconds": 45
        },
        {
            "id": "calculate_comprehensive_budget",
            "agent": "finance",
            "task": "calculate_trip_cost",
            "params": {
                "destination": "Japan",
                "duration": "7 days",
                "travelers": 2,
                "total_budget": 6000,
                "include_activities": True,
                "include_meals": True,
                "include_transportation": True
            },
            "after": ["find_international_flights", "find_accommodations", "research_activities"],
            "cost_estimate": 40,
            "retry_max": 2,
            "timeout_seconds": 50
        },
        {
            "id": "create_daily_itinerary",
            "agent": "travel",
            "task": "create_itinerary",
            "params": {
                "destination": "Japan",
                "duration": "7 days",
                "style": "cultural_immersion",
                "pace": "relaxed",
                "must_see": ["Senso-ji Temple", "Meiji Shrine", "Fushimi Inari", "Kinkaku-ji"]
            },
            "after": ["research_activities", "calculate_comprehensive_budget"],
            "cost_estimate": 50,
            "retry_max": 2,
            "timeout_seconds": 90
        },
        {
            "id": "generate_travel_guide",
            "agent": "compiler",
            "task": "compile_travel_plan",
            "params": {
                "format": "comprehensive_guide",
                "include_maps": True,
                "include_budget_breakdown": True,
                "include_packing_list": True,
                "include_cultural_tips": True
            },
            "after": ["create_daily_itinerary"],
            "cost_estimate": 35,
            "retry_max": 1,
            "timeout_seconds": 60
        }
    ]
}

# Parse and execute the workflow
script = parse_beescript(travel_workflow)
print(f"Created workflow: {script.goal}")
print(f"Total tasks: {len(script.subtasks)}")
print(f"Estimated cost: {sum(task.cost_estimate for task in script.subtasks)} credits")
```

## 🧠 Using Memory for Context

Let's enhance our workflow with memory to share context between tasks:

```python
from indra.memory import get_workflow_memory

# Create a session for this trip planning
session_id = "japan_trip_2024"
memory = get_workflow_memory(session_id)

# Store user preferences that all tasks can access
memory.store("traveler_preferences", {
    "budget_conscious": True,
    "cultural_focus": True,
    "dietary_restrictions": ["vegetarian"],
    "mobility_needs": None,
    "accommodation_style": "traditional_preferred"
}, task_id="init", agent="user")

memory.store("trip_constraints", {
    "max_budget": 6000,
    "travel_dates": "April 1-8, 2024",
    "departure_city": "San Francisco",
    "group_size": 2,
    "special_occasions": ["anniversary"]
}, task_id="init", agent="user")

# Now execute the workflow - tasks can access this context
client = OpenAI()
queen = Queen(client)
router = Router()
compiler = Compiler()

# Execute workflow with memory context
task_ids = [task.id for task in script.subtasks]
router.dispatch_tasks(script.subtasks)

# Monitor progress
import time
while not router.is_complete(task_ids):
    progress = router.monitor_progress()
    completed = sum(1 for status in progress.values() if status == "DONE")
    print(f"Progress: {completed}/{len(task_ids)} tasks completed")
    time.sleep(2)

# Compile results
results = compiler.compile_results(task_ids)
final_output = compiler.generate_final_output(results, script.goal, "japan_comprehensive_guide.json")

print(f"✅ Complete travel guide generated!")
print(f"📊 Tasks completed: {final_output['tasks_completed']}")
```

## 💰 Budget Management

Let's add sophisticated budget tracking:

```python
from indra.credits import get_credit_manager, TransactionType

# Set up credit management
credit_manager = get_credit_manager()
account = credit_manager.create_account(session_id, 300)  # 300 credit budget

print(f"💰 Starting budget: {account.current_balance} credits")

# Execute workflow with budget tracking
for task in script.subtasks:
    # Check if we can afford this task
    if not credit_manager.check_budget(session_id, task.cost_estimate):
        print(f"⚠️ Insufficient budget for {task.id} (needs {task.cost_estimate} credits)")
        continue
    
    # Charge for task execution
    success = credit_manager.charge_credits(
        session_id, 
        task.cost_estimate,
        TransactionType.TASK_EXECUTION,
        f"Execute {task.task} for {task.agent}",
        task_id=task.id,
        agent=task.agent
    )
    
    if success:
        print(f"💳 Charged {task.cost_estimate} credits for {task.id}")
        
        # Store task context in memory
        memory.store(f"task_{task.id}_cost", task.cost_estimate, task_id=task.id)
        memory.store(f"task_{task.id}_params", task.params, task_id=task.id)

# Check final spending
final_summary = credit_manager.get_account_summary(session_id)
print(f"\n💰 Budget Summary:")
print(f"   Initial budget: {final_summary['initial_budget']} credits")
print(f"   Total spent: {final_summary['total_spent']} credits")
print(f"   Remaining: {final_summary['current_balance']} credits")
print(f"   Budget utilization: {final_summary['budget_utilization']:.1f}%")

# Spending by agent
spending_by_agent = final_summary['spending_by_agent']
print(f"\n📊 Spending by Agent:")
for agent, amount in spending_by_agent.items():
    print(f"   {agent}: {amount} credits")
```

## 📊 Results Analysis

Let's analyze what our workflow produced:

```python
import json

# Load the comprehensive results
with open('japan_comprehensive_guide.json', 'r') as f:
    travel_guide = json.load(f)

print("🗾 Japan Travel Guide Generated!")
print(f"📋 Total tasks completed: {travel_guide['tasks_completed']}")

# Analyze each component
for result in travel_guide['results']:
    agent = result['worker']
    outputs = result['outputs']
    
    print(f"\n🤖 {agent.upper()} Agent Results:")
    
    if agent == 'travel':
        if 'flights' in outputs:
            flights = outputs['flights']
            print(f"   ✈️ Found {len(flights)} flight options")
            if flights:
                best_flight = min(flights, key=lambda f: f['price'])
                print(f"   💰 Best price: ${best_flight['price']} ({best_flight['airline']})")
        
        if 'hotels' in outputs:
            hotels = outputs['hotels']
            print(f"   🏨 Found {len(hotels)} accommodation options")
            if hotels:
                top_hotel = max(hotels, key=lambda h: h['rating'])
                print(f"   ⭐ Top rated: {top_hotel['name']} ({top_hotel['rating']} stars)")
        
        if 'activities' in outputs:
            activities = outputs['activities']
            print(f"   🎯 Suggested {len(activities)} activities")
        
        if 'itinerary' in outputs:
            itinerary = outputs['itinerary']
            print(f"   📅 Created {len(itinerary)} day itinerary")
    
    elif agent == 'finance':
        if 'estimated_cost' in outputs:
            cost = outputs['estimated_cost']
            status = outputs.get('budget_status', 'unknown')
            print(f"   💰 Estimated total cost: ${cost}")
            print(f"   📊 Budget status: {status}")
        
        if 'breakdown' in outputs:
            breakdown = outputs['breakdown']
            print(f"   📋 Cost breakdown:")
            for category, amount in breakdown.items():
                print(f"      {category}: ${amount}")

# Memory analysis
memory_stats = memory.get_stats()
print(f"\n🧠 Memory Usage:")
print(f"   Total entries: {memory_stats['total_entries']}")
print(f"   Agents involved: {', '.join(memory_stats['agents'])}")
print(f"   Tasks tracked: {len(memory_stats['tasks'])}")
```

## 🎨 Customization Examples

### Budget-Conscious Trip

```python
budget_trip = {
    "goal": "Plan an affordable 5-day trip to Thailand under $1500",
    "budget_credits": 150,
    "subtasks": [
        {
            "id": "find_budget_flights",
            "agent": "travel",
            "task": "find_flights",
            "params": {
                "destination": "Bangkok",
                "budget_range": "budget",
                "flexibility": "7_days"
            },
            "cost_estimate": 20
        },
        {
            "id": "find_hostels",
            "agent": "travel",
            "task": "find_hotels",
            "params": {
                "destination": "Bangkok",
                "budget_range": "budget",
                "accommodation_type": "hostel"
            },
            "after": ["find_budget_flights"],
            "cost_estimate": 15
        },
        {
            "id": "budget_activities",
            "agent": "travel",
            "task": "research_activities",
            "params": {
                "destination": "Thailand",
                "budget_per_day": 30,
                "focus": "free_and_cheap"
            },
            "after": ["find_hostels"],
            "cost_estimate": 20
        },
        {
            "id": "strict_budget_analysis",
            "agent": "finance",
            "task": "calculate_trip_cost",
            "params": {
                "total_budget": 1500,
                "strict_budget": True,
                "include_emergency_fund": True
            },
            "after": ["budget_activities"],
            "cost_estimate": 25
        }
    ]
}
```

### Luxury Experience

```python
luxury_trip = {
    "goal": "Plan a luxury 10-day European tour with premium experiences",
    "budget_credits": 400,
    "subtasks": [
        {
            "id": "premium_flights",
            "agent": "travel",
            "task": "find_flights",
            "params": {
                "destinations": ["Paris", "Rome", "Barcelona"],
                "class": "business",
                "flexibility": "minimal"
            },
            "cost_estimate": 50
        },
        {
            "id": "luxury_hotels",
            "agent": "travel",
            "task": "find_hotels",
            "params": {
                "budget_range": "luxury",
                "amenities": ["spa", "michelin_restaurant", "concierge"],
                "location": "city_center"
            },
            "after": ["premium_flights"],
            "cost_estimate": 45
        },
        {
            "id": "exclusive_experiences",
            "agent": "travel",
            "task": "research_activities",
            "params": {
                "type": "premium_experiences",
                "include": ["private_tours", "michelin_dining", "cultural_immersion"],
                "budget_per_day": 500
            },
            "after": ["luxury_hotels"],
            "cost_estimate": 60
        }
    ]
}
```

### Family Trip

```python
family_trip = {
    "goal": "Plan a family-friendly 7-day Disney World vacation for 4 people",
    "budget_credits": 250,
    "subtasks": [
        {
            "id": "family_flights",
            "agent": "travel",
            "task": "find_flights",
            "params": {
                "destination": "Orlando",
                "travelers": 4,
                "ages": [35, 33, 8, 5],
                "special_needs": ["child_meals", "early_boarding"]
            },
            "cost_estimate": 30
        },
        {
            "id": "family_hotel",
            "agent": "travel",
            "task": "find_hotels",
            "params": {
                "destination": "Disney World",
                "family_friendly": True,
                "amenities": ["pool", "kids_club", "kitchen"],
                "proximity": "on_property"
            },
            "after": ["family_flights"],
            "cost_estimate": 35
        },
        {
            "id": "disney_planning",
            "agent": "travel",
            "task": "create_itinerary",
            "params": {
                "destination": "Disney World",
                "duration": "7 days",
                "group_type": "family_with_young_kids",
                "priorities": ["character_meals", "must_do_rides", "rest_breaks"]
            },
            "after": ["family_hotel"],
            "cost_estimate": 40
        },
        {
            "id": "family_budget",
            "agent": "finance",
            "task": "calculate_trip_cost",
            "params": {
                "include_park_tickets": True,
                "include_character_dining": True,
                "include_souvenirs": True,
                "travelers": 4
            },
            "after": ["disney_planning"],
            "cost_estimate": 35
        }
    ]
}
```

## 🔧 Error Handling

Handle common issues gracefully:

```python
from indra.beescript import BeeScriptValidator

def execute_travel_workflow(workflow_data, session_id):
    try:
        # Parse and validate workflow
        script = parse_beescript(workflow_data)
        validator = BeeScriptValidator()
        
        if not validator.validate(script):
            print("❌ Workflow validation failed:")
            for error in validator.errors:
                print(f"   - {error}")
            return None
        
        # Set up resources
        memory = get_workflow_memory(session_id)
        credit_manager = get_credit_manager()
        account = credit_manager.get_or_create_account(session_id, script.budget_credits)
        
        # Execute workflow
        router = Router()
        compiler = Compiler()
        
        task_ids = [task.id for task in script.subtasks]
        router.dispatch_tasks(script.subtasks)
        
        # Wait with timeout
        completed = router.wait_for_completion(task_ids, timeout=script.timeout_minutes * 60)
        
        if completed:
            results = compiler.compile_results(task_ids)
            return compiler.generate_final_output(results, script.goal, f"{session_id}_results.json")
        else:
            print("⚠️ Workflow timed out - generating partial results")
            partial_results = compiler.compile_results(task_ids)
            return compiler.generate_final_output(partial_results, script.goal, f"{session_id}_partial.json")
            
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        return None

# Use the error-safe function
result = execute_travel_workflow(travel_workflow, "safe_japan_trip")
if result:
    print(f"✅ Travel planning completed: {result['tasks_completed']} tasks")
else:
    print("❌ Travel planning failed")
```

## 🎯 Next Steps

Now that you've seen comprehensive travel planning:

1. **Try the examples** - Run the code snippets above
2. **Customize workflows** - Modify the BeeScript for your needs
3. **Explore other examples** - Check out [Budget Analysis](budget-analysis.md)
4. **Learn advanced techniques** - See [Advanced BeeScript Guide](../guides/advanced-beescript.md)

## 💡 Pro Tips

- **Start simple** - Begin with basic workflows and add complexity gradually
- **Use memory effectively** - Share context between tasks for better results
- **Monitor budgets** - Track credit usage to avoid overspending
- **Handle errors gracefully** - Always validate workflows and handle timeouts
- **Customize for your needs** - Modify the examples for your specific use cases

---

*Ready for more examples? Check out [Budget Analysis](budget-analysis.md) or [Complex Workflows](complex-workflows.md)!*