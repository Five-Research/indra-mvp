"""
Memory System - Session-based context storage for task workflows.

Provides persistent memory across task execution within a workflow session,
allowing agents to share context and build upon previous results.
"""

import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MemoryEntry:
    """Individual memory entry with metadata."""
    key: str
    value: Any
    timestamp: float
    task_id: Optional[str] = None
    agent: Optional[str] = None
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)


class WorkflowMemory:
    """Memory system for a single workflow session."""
    
    def __init__(self, session_id: str, max_entries: int = 1000):
        self.session_id = session_id
        self.max_entries = max_entries
        self.entries: Dict[str, MemoryEntry] = {}
        self.created_at = time.time()
        self.last_accessed = time.time()
    
    def store(self, key: str, value: Any, task_id: Optional[str] = None, 
              agent: Optional[str] = None) -> None:
        """Store a value in memory."""
        # Evict oldest entries if at capacity
        if len(self.entries) >= self.max_entries:
            self._evict_oldest()
        
        entry = MemoryEntry(
            key=key,
            value=value,
            timestamp=time.time(),
            task_id=task_id,
            agent=agent
        )
        
        self.entries[key] = entry
        self.last_accessed = time.time()
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from memory."""
        entry = self.entries.get(key)
        if entry:
            entry.access_count += 1
            entry.last_accessed = time.time()
            self.last_accessed = time.time()
            return entry.value
        return None
    
    def get_by_task(self, task_id: str) -> Dict[str, Any]:
        """Get all memory entries created by a specific task."""
        result = {}
        for key, entry in self.entries.items():
            if entry.task_id == task_id:
                entry.access_count += 1
                entry.last_accessed = time.time()
                result[key] = entry.value
        
        if result:
            self.last_accessed = time.time()
        
        return result
    
    def get_by_agent(self, agent: str) -> Dict[str, Any]:
        """Get all memory entries created by a specific agent."""
        result = {}
        for key, entry in self.entries.items():
            if entry.agent == agent:
                entry.access_count += 1
                entry.last_accessed = time.time()
                result[key] = entry.value
        
        if result:
            self.last_accessed = time.time()
        
        return result
    
    def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """List all keys, optionally filtered by pattern."""
        keys = list(self.entries.keys())
        
        if pattern:
            keys = [k for k in keys if pattern in k]
        
        return sorted(keys)
    
    def delete(self, key: str) -> bool:
        """Delete a memory entry."""
        if key in self.entries:
            del self.entries[key]
            self.last_accessed = time.time()
            return True
        return False
    
    def clear(self) -> None:
        """Clear all memory entries."""
        self.entries.clear()
        self.last_accessed = time.time()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        if not self.entries:
            return {
                "total_entries": 0,
                "memory_age_seconds": time.time() - self.created_at,
                "last_accessed_seconds_ago": time.time() - self.last_accessed,
                "most_accessed_key": None,
                "agents": [],
                "tasks": []
            }
        
        # Calculate statistics
        most_accessed = max(self.entries.values(), key=lambda e: e.access_count)
        agents = list(set(e.agent for e in self.entries.values() if e.agent))
        tasks = list(set(e.task_id for e in self.entries.values() if e.task_id))
        
        return {
            "total_entries": len(self.entries),
            "memory_age_seconds": time.time() - self.created_at,
            "last_accessed_seconds_ago": time.time() - self.last_accessed,
            "most_accessed_key": most_accessed.key,
            "most_accessed_count": most_accessed.access_count,
            "agents": agents,
            "tasks": tasks
        }
    
    def _evict_oldest(self) -> None:
        """Evict the oldest entry based on last access time."""
        if not self.entries:
            return
        
        # Find entry with oldest last_accessed time
        oldest_key = min(self.entries.keys(), 
                        key=lambda k: self.entries[k].last_accessed)
        del self.entries[oldest_key]


class MemoryManager:
    """Manages memory sessions for multiple workflows."""
    
    def __init__(self, storage_dir: str = "memory", max_sessions: int = 100):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.max_sessions = max_sessions
        self.sessions: Dict[str, WorkflowMemory] = {}
    
    def create_session(self, session_id: str) -> WorkflowMemory:
        """Create a new memory session."""
        # Evict old sessions if at capacity
        if len(self.sessions) >= self.max_sessions:
            self._evict_oldest_session()
        
        memory = WorkflowMemory(session_id)
        self.sessions[session_id] = memory
        return memory
    
    def get_session(self, session_id: str) -> Optional[WorkflowMemory]:
        """Get an existing memory session."""
        return self.sessions.get(session_id)
    
    def get_or_create_session(self, session_id: str) -> WorkflowMemory:
        """Get existing session or create new one."""
        session = self.get_session(session_id)
        if session is None:
            session = self.create_session(session_id)
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a memory session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            
            # Also delete persisted file if it exists
            session_file = self.storage_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            
            return True
        return False
    
    def persist_session(self, session_id: str) -> bool:
        """Persist a session to disk."""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        try:
            session_data = {
                "session_id": session.session_id,
                "created_at": session.created_at,
                "last_accessed": session.last_accessed,
                "entries": {
                    key: {
                        "key": entry.key,
                        "value": entry.value,
                        "timestamp": entry.timestamp,
                        "task_id": entry.task_id,
                        "agent": entry.agent,
                        "access_count": entry.access_count,
                        "last_accessed": entry.last_accessed
                    }
                    for key, entry in session.entries.items()
                }
            }
            
            session_file = self.storage_dir / f"{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            return True
        except Exception:
            return False
    
    def load_session(self, session_id: str) -> Optional[WorkflowMemory]:
        """Load a session from disk."""
        session_file = self.storage_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Recreate memory session
            memory = WorkflowMemory(session_id)
            memory.created_at = session_data["created_at"]
            memory.last_accessed = session_data["last_accessed"]
            
            # Recreate entries
            for key, entry_data in session_data["entries"].items():
                entry = MemoryEntry(
                    key=entry_data["key"],
                    value=entry_data["value"],
                    timestamp=entry_data["timestamp"],
                    task_id=entry_data.get("task_id"),
                    agent=entry_data.get("agent"),
                    access_count=entry_data.get("access_count", 0),
                    last_accessed=entry_data.get("last_accessed", entry_data["timestamp"])
                )
                memory.entries[key] = entry
            
            self.sessions[session_id] = memory
            return memory
            
        except Exception:
            return None
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up old sessions."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned_count = 0
        
        # Clean up in-memory sessions
        to_delete = []
        for session_id, session in self.sessions.items():
            if session.last_accessed < cutoff_time:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            self.delete_session(session_id)
            cleaned_count += 1
        
        # Clean up persisted sessions
        for session_file in self.storage_dir.glob("*.json"):
            try:
                if session_file.stat().st_mtime < cutoff_time:
                    session_file.unlink()
                    cleaned_count += 1
            except OSError:
                continue
        
        return cleaned_count
    
    def get_all_sessions(self) -> List[str]:
        """Get list of all active session IDs."""
        return list(self.sessions.keys())
    
    def _evict_oldest_session(self) -> None:
        """Evict the oldest session based on last access time."""
        if not self.sessions:
            return
        
        oldest_session_id = min(self.sessions.keys(),
                               key=lambda sid: self.sessions[sid].last_accessed)
        
        # Persist before evicting
        self.persist_session(oldest_session_id)
        del self.sessions[oldest_session_id]


# Global memory manager instance
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


def get_workflow_memory(session_id: str) -> WorkflowMemory:
    """Convenience function to get workflow memory."""
    manager = get_memory_manager()
    return manager.get_or_create_session(session_id)