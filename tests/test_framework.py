#!/usr/bin/env python3
"""Simple test script for Indra framework."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import tempfile

def test_basic_functionality():
    """Test basic framework functionality."""
    print("🧪 Testing Indra framework...")
    
    # Test imports
    try:
        from indra.models import Task, TaskStatus, WorkerResult
        from indra.base_worker import WORKER_REGISTRY
        import indra.workers
        print("✅ Imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test task creation
    task = Task(id="test-1", task="test", worker="travel")
    assert task.status == TaskStatus.PENDING
    print("✅ Task creation works")
    
    # Test worker registry
    assert "travel" in WORKER_REGISTRY
    assert "finance" in WORKER_REGISTRY
    print("✅ Workers registered")
    
    # Test worker execution
    worker_class = WORKER_REGISTRY["travel"]
    worker = worker_class("travel")
    result = worker.execute(destination="Paris")
    assert isinstance(result, dict)
    print("✅ Worker execution works")
    
    return True

def main():
    """Run tests."""
    print("🚀 Running Indra Tests")
    print("=" * 30)
    
    if test_basic_functionality():
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n❌ Tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)