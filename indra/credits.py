"""
Credit System - Budget management and cost tracking for workflows.

Implements a simple credit-based system for tracking resource usage
and enforcing budget constraints during workflow execution.
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class TransactionType(str, Enum):
    """Types of credit transactions."""
    TASK_EXECUTION = "task_execution"
    TASK_RETRY = "task_retry"
    MEMORY_STORAGE = "memory_storage"
    API_CALL = "api_call"
    TIMEOUT_PENALTY = "timeout_penalty"
    REFUND = "refund"


@dataclass
class CreditTransaction:
    """Individual credit transaction record."""
    transaction_id: str
    session_id: str
    transaction_type: TransactionType
    amount: int  # Positive for charges, negative for refunds
    description: str
    task_id: Optional[str] = None
    agent: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class CreditAccount:
    """Credit account for a workflow session."""
    session_id: str
    initial_budget: int
    current_balance: int
    total_spent: int = 0
    transactions: List[CreditTransaction] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)


class CreditManager:
    """Manages credit accounts and transactions."""
    
    def __init__(self):
        self.accounts: Dict[str, CreditAccount] = {}
        self.transaction_counter = 0
    
    def create_account(self, session_id: str, initial_budget: int) -> CreditAccount:
        """Create a new credit account."""
        if initial_budget <= 0:
            raise ValueError("Initial budget must be positive")
        
        account = CreditAccount(
            session_id=session_id,
            initial_budget=initial_budget,
            current_balance=initial_budget
        )
        
        self.accounts[session_id] = account
        return account
    
    def get_account(self, session_id: str) -> Optional[CreditAccount]:
        """Get an existing credit account."""
        return self.accounts.get(session_id)
    
    def get_or_create_account(self, session_id: str, initial_budget: int = 100) -> CreditAccount:
        """Get existing account or create new one."""
        account = self.get_account(session_id)
        if account is None:
            account = self.create_account(session_id, initial_budget)
        return account
    
    def charge_credits(self, session_id: str, amount: int, 
                      transaction_type: TransactionType, description: str,
                      task_id: Optional[str] = None, agent: Optional[str] = None,
                      metadata: Optional[Dict[str, str]] = None) -> bool:
        """Charge credits from an account."""
        account = self.get_account(session_id)
        if not account:
            return False
        
        if amount <= 0:
            raise ValueError("Charge amount must be positive")
        
        if account.current_balance < amount:
            return False  # Insufficient funds
        
        # Create transaction
        self.transaction_counter += 1
        transaction = CreditTransaction(
            transaction_id=f"tx-{self.transaction_counter:06d}",
            session_id=session_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            task_id=task_id,
            agent=agent,
            metadata=metadata or {}
        )
        
        # Update account
        account.current_balance -= amount
        account.total_spent += amount
        account.transactions.append(transaction)
        account.last_activity = time.time()
        
        return True
    
    def refund_credits(self, session_id: str, amount: int, description: str,
                      task_id: Optional[str] = None, agent: Optional[str] = None) -> bool:
        """Refund credits to an account."""
        account = self.get_account(session_id)
        if not account:
            return False
        
        if amount <= 0:
            raise ValueError("Refund amount must be positive")
        
        # Don't refund more than was spent
        refund_amount = min(amount, account.total_spent)
        if refund_amount <= 0:
            return False
        
        # Create refund transaction
        self.transaction_counter += 1
        transaction = CreditTransaction(
            transaction_id=f"tx-{self.transaction_counter:06d}",
            session_id=session_id,
            transaction_type=TransactionType.REFUND,
            amount=-refund_amount,  # Negative for refunds
            description=description,
            task_id=task_id,
            agent=agent
        )
        
        # Update account
        account.current_balance += refund_amount
        account.total_spent -= refund_amount
        account.transactions.append(transaction)
        account.last_activity = time.time()
        
        return True
    
    def check_budget(self, session_id: str, required_amount: int) -> bool:
        """Check if account has sufficient budget."""
        account = self.get_account(session_id)
        if not account:
            return False
        
        return account.current_balance >= required_amount
    
    def get_balance(self, session_id: str) -> Optional[int]:
        """Get current account balance."""
        account = self.get_account(session_id)
        return account.current_balance if account else None
    
    def get_spending_by_agent(self, session_id: str) -> Dict[str, int]:
        """Get spending breakdown by agent."""
        account = self.get_account(session_id)
        if not account:
            return {}
        
        spending = {}
        for transaction in account.transactions:
            if transaction.amount > 0 and transaction.agent:  # Only charges, not refunds
                spending[transaction.agent] = spending.get(transaction.agent, 0) + transaction.amount
        
        return spending
    
    def get_spending_by_task(self, session_id: str) -> Dict[str, int]:
        """Get spending breakdown by task."""
        account = self.get_account(session_id)
        if not account:
            return {}
        
        spending = {}
        for transaction in account.transactions:
            if transaction.amount > 0 and transaction.task_id:  # Only charges, not refunds
                spending[transaction.task_id] = spending.get(transaction.task_id, 0) + transaction.amount
        
        return spending
    
    def get_transaction_history(self, session_id: str, 
                               limit: Optional[int] = None) -> List[CreditTransaction]:
        """Get transaction history for an account."""
        account = self.get_account(session_id)
        if not account:
            return []
        
        transactions = sorted(account.transactions, key=lambda t: t.timestamp, reverse=True)
        
        if limit:
            transactions = transactions[:limit]
        
        return transactions
    
    def get_account_summary(self, session_id: str) -> Optional[Dict[str, any]]:
        """Get comprehensive account summary."""
        account = self.get_account(session_id)
        if not account:
            return None
        
        # Calculate statistics
        total_transactions = len(account.transactions)
        charges = sum(t.amount for t in account.transactions if t.amount > 0)
        refunds = sum(-t.amount for t in account.transactions if t.amount < 0)
        
        # Get spending by type
        spending_by_type = {}
        for transaction in account.transactions:
            if transaction.amount > 0:
                tx_type = transaction.transaction_type.value
                spending_by_type[tx_type] = spending_by_type.get(tx_type, 0) + transaction.amount
        
        return {
            "session_id": account.session_id,
            "initial_budget": account.initial_budget,
            "current_balance": account.current_balance,
            "total_spent": account.total_spent,
            "budget_utilization": (account.total_spent / account.initial_budget) * 100,
            "total_transactions": total_transactions,
            "total_charges": charges,
            "total_refunds": refunds,
            "spending_by_type": spending_by_type,
            "spending_by_agent": self.get_spending_by_agent(session_id),
            "spending_by_task": self.get_spending_by_task(session_id),
            "account_age_seconds": time.time() - account.created_at,
            "last_activity_seconds_ago": time.time() - account.last_activity
        }
    
    def cleanup_old_accounts(self, max_age_hours: int = 24) -> int:
        """Clean up old inactive accounts."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned_count = 0
        
        to_delete = []
        for session_id, account in self.accounts.items():
            if account.last_activity < cutoff_time:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            del self.accounts[session_id]
            cleaned_count += 1
        
        return cleaned_count


# Cost estimation functions
def estimate_task_cost(agent: str, task_type: str, params: Dict[str, any]) -> int:
    """Estimate the cost of executing a task."""
    # Base costs by agent type
    base_costs = {
        "travel": 15,
        "finance": 12,
        "compiler": 8,
        "queen": 25
    }
    
    base_cost = base_costs.get(agent, 10)
    
    # Adjust based on task complexity
    complexity_multipliers = {
        "find_flights": 1.5,
        "find_hotels": 1.3,
        "calculate_trip_cost": 1.2,
        "travel_planning": 2.0,
        "compile_results": 1.1
    }
    
    multiplier = complexity_multipliers.get(task_type, 1.0)
    
    # Adjust based on parameters
    param_cost = 0
    if isinstance(params, dict):
        # More parameters = slightly higher cost
        param_cost = len(params) * 0.5
    
    estimated_cost = int(base_cost * multiplier + param_cost)
    return max(estimated_cost, 1)  # Minimum cost of 1


def estimate_retry_cost(base_cost: int, retry_count: int) -> int:
    """Estimate the cost of a retry (typically higher than base cost)."""
    # Exponential backoff for retry costs
    retry_multiplier = 1.5 ** retry_count
    return int(base_cost * retry_multiplier)


# Global credit manager instance
_credit_manager = None

def get_credit_manager() -> CreditManager:
    """Get the global credit manager instance."""
    global _credit_manager
    if _credit_manager is None:
        _credit_manager = CreditManager()
    return _credit_manager