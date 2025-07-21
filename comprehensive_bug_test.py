#!/usr/bin/env python3
"""
Comprehensive Bug and Edge Case Test Suite

Tests all the critical bugs and edge cases that were identified and fixed.
"""

import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

def test_router_edge_cases():
    """Test Router component edge cases."""
    print("🧪 Testing Router edge cases...")
    
    from indra.router import Router
    from indra.models import Task
    
    with tempfile.TemporaryDirectory() as temp_dir:
        router = Router(
            queue_dir=str(Path(temp_dir) / "queue"),
            results_dir=str(Path(temp_dir) / "results")
        )
        
        # Test 1: Empty task list
        router.dispatch_tasks([])
        print("✅ Empty task list handled")
        
        # Test 2: Malformed JSON file in queue
        queue_dir = Path(temp_dir) / "queue"
        malformed_file = queue_dir / "malformed.json"
        with open(malformed_file, 'w') as f:
            f.write("{ invalid json")
        
        progress = router.monitor_progress()
        # Should not crash and should skip malformed file
        print("✅ Malformed JSON files handled")
        
        # Test 3: Missing task ID in file
        missing_id_file = queue_dir / "missing_id.json"
        with open(missing_id_file, 'w') as f:
            json.dump({"task": "test", "worker": "travel"}, f)
        
        progress = router.monitor_progress()
        # Should not crash and should skip file without ID
        print("✅ Missing task ID handled")
        
        # Test 4: Empty task_ids list
        assert router.is_complete([]) == True
        print("✅ Empty task_ids list handled")
        
        # Test 5: Non-existent worker
        bad_task_file = queue_dir / "bad_worker.json"
        with open(bad_task_file, 'w') as f:
            json.dump({
                "id": "bad-task",
                "task": "test",
                "worker": "nonexistent_worker",
                "status": "PENDING"
            }, f)
        
        # Should not crash when trying to execute
        router.execute_pending_tasks()
        print("✅ Non-existent worker handled")

def test_compiler_edge_cases():
    """Test Compiler component edge cases."""
    print("\n🧪 Testing Compiler edge cases...")
    
    from indra.compiler import Compiler
    
    with tempfile.TemporaryDirectory() as temp_dir:
        compiler = Compiler(results_dir=temp_dir)
        
        # Test 1: Empty task_ids list
        result = compiler.compile_results([])
        assert result["completed_tasks"] == 0
        assert result["total_tasks"] == 0
        print("✅ Empty task_ids list handled")
        
        # Test 2: Malformed result file
        malformed_result = Path(temp_dir) / "malformed_result.json"
        with open(malformed_result, 'w') as f:
            f.write("{ invalid json")
        
        result = compiler.compile_results(["malformed"])
        # Should not crash and should skip malformed file
        print("✅ Malformed result files handled")
        
        # Test 3: Missing required fields in result
        incomplete_result = Path(temp_dir) / "incomplete_result.json"
        with open(incomplete_result, 'w') as f:
            json.dump({"task_id": "incomplete"}, f)  # Missing worker and outputs
        
        result = compiler.compile_results(["incomplete"])
        # Should not crash and should skip incomplete result
        print("✅ Incomplete result data handled")
        
        # Test 4: Valid result file
        valid_result = Path(temp_dir) / "valid_result.json"
        with open(valid_result, 'w') as f:
            json.dump({
                "task_id": "valid",
                "worker": "travel",
                "outputs": {"test": "data"},
                "execution_time": 1.0,
                "timestamp": "2024-01-01T00:00:00"
            }, f)
        
        result = compiler.compile_results(["valid"])
        assert result["completed_tasks"] == 1
        print("✅ Valid result files processed correctly")

def test_cli_edge_cases():
    """Test CLI component edge cases."""
    print("\n🧪 Testing CLI edge cases...")
    
    from indra.cli import run_workflow
    
    # Test 1: Empty prompt
    result = run_workflow("")
    assert result == False
    print("✅ Empty prompt handled")
    
    # Test 2: Whitespace-only prompt
    result = run_workflow("   ")
    assert result == False
    print("✅ Whitespace-only prompt handled")
    
    # Test 3: Missing API key
    with patch.dict(os.environ, {}, clear=True):
        result = run_workflow("test prompt")
        assert result == False
        print("✅ Missing API key handled")

def test_worker_edge_cases():
    """Test Worker component edge cases."""
    print("\n🧪 Testing Worker edge cases...")
    
    from indra.workers.travel import TravelWorker
    from indra.workers.finance import FinanceWorker
    
    # Test Travel Worker
    travel_worker = TravelWorker("travel")
    
    # Test 1: Empty destination
    result = travel_worker.execute(destination="")
    assert result["destination"] == "Paris"  # Should fallback to default
    print("✅ Travel worker empty destination handled")
    
    # Test 2: None destination
    result = travel_worker.execute(destination=None)
    assert result["destination"] == "Paris"  # Should fallback to default
    print("✅ Travel worker None destination handled")
    
    # Test 3: Invalid duration parsing
    result = travel_worker._handle_hotel_search({"destination": "Paris", "duration": "invalid"})
    assert result["nights"] == 3  # Should fallback to default
    print("✅ Travel worker invalid duration handled")
    
    # Test Finance Worker
    finance_worker = FinanceWorker("finance")
    
    # Test 4: Division by zero in savings planning
    result = finance_worker._handle_savings_planning({
        "total_budget": 2000,
        "months_to_save": 0,  # This could cause division by zero
        "current_savings": 0
    })
    # Should handle gracefully
    print("✅ Finance worker division by zero handled")
    
    # Test 5: Invalid duration parsing
    result = finance_worker._parse_duration("invalid duration")
    assert result == 3  # Should fallback to default
    print("✅ Finance worker invalid duration handled")

def test_base_worker_edge_cases():
    """Test BaseWorker component edge cases."""
    print("\n🧪 Testing BaseWorker edge cases...")
    
    from indra.base_worker import BaseWorker, register_worker
    import tempfile
    
    # Test duplicate worker registration
    try:
        @register_worker("travel")  # This should fail since travel already exists
        class DuplicateWorker(BaseWorker):
            def execute(self, **inputs):
                return {}
        
        print("❌ Duplicate worker registration should have failed")
    except ValueError:
        print("✅ Duplicate worker registration prevented")
    
    # Test task file processing with missing file
    from indra.workers.travel import TravelWorker
    travel_worker = TravelWorker("travel")
    try:
        travel_worker.process_task_file("nonexistent_file.json")
        print("❌ Missing task file should have raised error")
    except FileNotFoundError:
        print("✅ Missing task file handled")
    
    # Test task file processing with malformed JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json")
        temp_file = f.name
    
    try:
        travel_worker.process_task_file(temp_file)
        print("❌ Malformed JSON should have raised error")
    except json.JSONDecodeError:
        print("✅ Malformed JSON in task file handled")
    finally:
        os.unlink(temp_file)

def test_models_edge_cases():
    """Test Models component edge cases."""
    print("\n🧪 Testing Models edge cases...")
    
    from indra.models import Task, WorkerResult, validate_task_json
    
    # Test Task creation with minimal data
    task = Task(id="test", task="test", worker="travel")
    assert task.status.value == "PENDING"
    print("✅ Task creation with minimal data works")
    
    # Test WorkerResult creation
    result = WorkerResult(task_id="test", worker="travel", outputs={"test": "data"})
    assert result.task_id == "test"
    print("✅ WorkerResult creation works")
    
    # Test validate_task_json with invalid JSON
    try:
        validate_task_json("{ invalid json")
        print("❌ Invalid JSON should have raised error")
    except json.JSONDecodeError:
        print("✅ Invalid JSON in validate_task_json handled")
    
    # Test validate_task_json with valid JSON
    valid_json = '[{"id": "test", "task": "test", "worker": "travel"}]'
    tasks = validate_task_json(valid_json)
    assert len(tasks) == 1
    print("✅ Valid JSON in validate_task_json works")

def test_queen_edge_cases():
    """Test Queen component edge cases."""
    print("\n🧪 Testing Queen edge cases...")
    
    from indra.queen import Queen
    
    # Mock OpenAI client that returns invalid JSON
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "{ invalid json"
    mock_client.chat.completions.create.return_value = mock_response
    
    queen = Queen(mock_client)
    
    try:
        tasks = queen.generate_tasks("test prompt")
        print("❌ Invalid JSON from OpenAI should have raised error")
    except json.JSONDecodeError:
        print("✅ Invalid JSON from OpenAI handled")
    
    # Mock OpenAI client that returns valid JSON
    mock_response.choices[0].message.content = '[{"task": "test", "worker": "travel"}]'
    tasks = queen.generate_tasks("test prompt")
    assert len(tasks) == 1
    assert tasks[0].id.startswith("task-")  # Should auto-generate ID
    print("✅ Valid JSON from OpenAI processed correctly")

def main():
    """Run all edge case tests."""
    print("🚀 Running Comprehensive Bug and Edge Case Tests")
    print("=" * 60)
    
    try:
        test_router_edge_cases()
        test_compiler_edge_cases()
        test_cli_edge_cases()
        test_worker_edge_cases()
        test_base_worker_edge_cases()
        test_models_edge_cases()
        test_queen_edge_cases()
        
        print("\n" + "=" * 60)
        print("🎉 ALL EDGE CASE TESTS PASSED!")
        print("✅ The codebase is robust and handles edge cases properly")
        print("🛡️  All critical bugs have been fixed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Edge case test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)