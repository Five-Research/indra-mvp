#!/usr/bin/env python3
"""
Integration Test - Test the complete Indra workflow without API calls

This test validates that all components work together properly using mock data.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

def test_complete_workflow():
    """Test the complete workflow from end to end."""
    print("🧪 Testing Complete Workflow Integration...")
    
    from indra.queen import Queen
    from indra.router import Router
    from indra.compiler import Compiler
    from indra.models import Task, TaskStatus
    
    # Mock OpenAI client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = '''[
        {
            "task": "research_destination",
            "worker": "travel",
            "inputs": {"destination": "Paris", "duration": "3 days"}
        },
        {
            "task": "calculate_budget",
            "worker": "finance", 
            "inputs": {"destination": "Paris", "budget": 2000}
        }
    ]'''
    mock_client.chat.completions.create.return_value = mock_response
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize components
        queen = Queen(mock_client)
        router = Router(
            queue_dir=str(Path(temp_dir) / "queue"),
            results_dir=str(Path(temp_dir) / "results")
        )
        compiler = Compiler(results_dir=str(Path(temp_dir) / "results"))
        
        # Step 1: Generate tasks
        tasks = queen.generate_tasks("Plan a 3-day trip to Paris with $2000 budget")
        assert len(tasks) == 2
        assert all(isinstance(task, Task) for task in tasks)
        print("✅ Task generation works")
        
        # Step 2: Dispatch tasks
        task_ids = [task.id for task in tasks]
        router.dispatch_tasks(tasks)
        
        # Verify tasks were dispatched
        queue_files = list(Path(temp_dir, "queue").glob("*.json"))
        assert len(queue_files) == 2
        print("✅ Task dispatch works")
        
        # Step 3: Execute tasks (simulate)
        router.execute_pending_tasks()
        
        # Verify results were created
        result_files = list(Path(temp_dir, "results").glob("*.json"))
        assert len(result_files) == 2
        print("✅ Task execution works")
        
        # Step 4: Check completion
        completed = router.is_complete(task_ids)
        assert completed == True
        print("✅ Completion detection works")
        
        # Step 5: Compile results
        compiled_data = compiler.compile_results(task_ids)
        assert compiled_data["completed_tasks"] == 2
        assert compiled_data["total_tasks"] == 2
        assert len(compiled_data["results"]) == 2
        print("✅ Result compilation works")
        
        # Step 6: Generate final output
        output_file = Path(temp_dir) / "final_result.json"
        final_output = compiler.generate_final_output(
            compiled_data, 
            "Plan a 3-day trip to Paris with $2000 budget",
            str(output_file)
        )
        
        assert output_file.exists()
        assert final_output["tasks_completed"] == 2
        print("✅ Final output generation works")
        
        # Verify final output structure
        with open(output_file) as f:
            final_data = json.load(f)
        
        print(f"Final data keys: {list(final_data.keys())}")
        required_keys = ["prompt", "tasks_completed", "results"]
        missing_keys = [key for key in required_keys if key not in final_data]
        if missing_keys:
            print(f"Missing keys: {missing_keys}")
        assert all(key in final_data for key in required_keys)
        print("✅ Final output structure is correct")

def test_beescript_workflow():
    """Test BeeScript workflow generation and execution."""
    print("\n🧪 Testing BeeScript Workflow...")
    
    from indra.queen import Queen
    from indra.beescript import BeeScriptExecutor, BeeScriptValidator
    
    # Mock OpenAI client for BeeScript generation
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = '''{
        "goal": "Plan a trip to Tokyo",
        "budget_credits": 100,
        "timeout_minutes": 10,
        "subtasks": [
            {
                "id": "research",
                "agent": "travel",
                "task": "research_destination",
                "params": {"destination": "Tokyo"},
                "cost_estimate": 20,
                "retry_max": 2
            },
            {
                "id": "flights",
                "agent": "travel",
                "task": "find_flights", 
                "params": {"destination": "Tokyo"},
                "after": ["research"],
                "cost_estimate": 30,
                "retry_max": 3
            }
        ]
    }'''
    mock_client.chat.completions.create.return_value = mock_response
    
    queen = Queen(mock_client)
    
    # Generate BeeScript
    script = queen.generate_beescript("Plan a trip to Tokyo", budget_credits=100)
    assert script.goal == "Plan a trip to Tokyo"
    assert len(script.subtasks) == 2
    print("✅ BeeScript generation works")
    
    # Validate BeeScript
    validator = BeeScriptValidator()
    is_valid = validator.validate(script)
    assert is_valid == True
    print("✅ BeeScript validation works")
    
    # Get execution order
    executor = BeeScriptExecutor()
    execution_order = executor.get_execution_order(script)
    expected_order = [["research"], ["flights"]]
    assert execution_order == expected_order
    print("✅ BeeScript execution order works")

def test_memory_and_credits():
    """Test memory and credit systems."""
    print("\n🧪 Testing Memory and Credit Systems...")
    
    from indra.memory import WorkflowMemory, get_workflow_memory
    from indra.credits import CreditManager, get_credit_manager, TransactionType
    
    # Test memory system
    memory = get_workflow_memory("test-session")
    memory.store("destination", "Tokyo", task_id="task1", agent="travel")
    memory.store("budget", 3000, task_id="task2", agent="finance")
    
    assert memory.retrieve("destination") == "Tokyo"
    assert memory.retrieve("budget") == 3000
    
    stats = memory.get_stats()
    assert stats["total_entries"] == 2
    print("✅ Memory system works")
    
    # Test credit system
    credit_manager = get_credit_manager()
    account = credit_manager.create_account("test-session", 100)
    
    assert account.current_balance == 100
    
    success = credit_manager.charge_credits(
        "test-session", 25, TransactionType.TASK_EXECUTION, "Test task"
    )
    assert success == True
    assert credit_manager.get_balance("test-session") == 75
    print("✅ Credit system works")

def main():
    """Run all integration tests."""
    print("🚀 Running Integration Tests")
    print("=" * 50)
    
    try:
        test_complete_workflow()
        test_beescript_workflow()
        test_memory_and_credits()
        
        print("\n" + "=" * 50)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Complete workflow integration verified")
        print("✅ BeeScript system operational")
        print("✅ Memory and credit systems functional")
        print("\n🚀 Indra MVP is ready for production!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)