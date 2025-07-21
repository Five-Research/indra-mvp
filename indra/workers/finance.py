"""Finance Worker - Handles financial calculations with stubbed data."""

import random
from typing import Dict, Any, List
from datetime import datetime
from ..base_worker import BaseWorker, register_worker


@register_worker("finance")
class FinanceWorker(BaseWorker):
    """Finance worker that handles cost calculations and budgeting."""
    
    def __init__(self, worker_name: str = "finance", results_dir: str = "results"):
        """Initialize the finance worker."""
        super().__init__(worker_name, results_dir)
        
        # Cost data for different destinations and categories
        self.destination_multipliers = {
            "Paris": 1.3,
            "London": 1.4,
            "Tokyo": 1.2,
            "New York": 1.5,
            "Sydney": 1.1,
            "Dubai": 1.0,
            "Singapore": 0.9,
            "Barcelona": 0.8,
            "Bangkok": 0.5,
            "Prague": 0.6,
            "Budapest": 0.5,
            "Lisbon": 0.7
        }
        
        # Base daily costs in USD
        self.base_costs = {
            "accommodation": {"budget": 60, "mid_range": 150, "luxury": 400},
            "food": {"budget": 25, "mid_range": 60, "luxury": 120},
            "transportation": {"budget": 15, "mid_range": 30, "luxury": 80},
            "activities": {"budget": 20, "mid_range": 50, "luxury": 150},
            "miscellaneous": {"budget": 10, "mid_range": 25, "luxury": 50}
        }
        
        # Exchange rates (stubbed for demo)
        self.exchange_rates = {
            "USD": 1.0,
            "EUR": 0.85,
            "GBP": 0.75,
            "JPY": 110.0,
            "AUD": 1.35,
            "AED": 3.67,
            "SGD": 1.35
        }
    
    def execute(self, **inputs) -> Dict[str, Any]:
        """Execute finance-related tasks."""
        task_type = inputs.get('task', 'budget_analysis')
        
        # Route to specific task handlers
        if task_type in ['calculate_trip_cost', 'trip_budget']:
            return self._handle_trip_cost_calculation(inputs)
        elif task_type in ['budget_breakdown', 'expense_breakdown']:
            return self._handle_budget_breakdown(inputs)
        elif task_type in ['savings_plan', 'financial_planning']:
            return self._handle_savings_planning(inputs)
        elif task_type in ['currency_conversion', 'exchange_rates']:
            return self._handle_currency_conversion(inputs)
        else:
            # General financial analysis - simple fallback
            destination = inputs.get('destination', 'Paris')
            duration = inputs.get('duration', '3 days')
            total_budget = inputs.get('total_budget', 2000)
            
            # Simple cost calculation
            estimated_cost = 1500  # Stubbed estimate
            budget_status = "within_budget" if total_budget >= estimated_cost else "over_budget"
            
            return {
                "task_type": task_type,
                "destination": destination,
                "duration": duration,
                "total_budget": total_budget,
                "estimated_cost": estimated_cost,
                "budget_status": budget_status,
                "daily_cost": estimated_cost // 3,  # Rough daily estimate
                "breakdown": {
                    "accommodation": 450,
                    "food": 300,
                    "transportation": 200,
                    "activities": 350,
                    "flights": 200
                },
                "recommendation": f"Budget looks {budget_status.replace('_', ' ')}"
            }
    
    def _handle_trip_cost_calculation(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive trip costs."""
        destination = inputs.get('destination', 'Unknown')
        duration = inputs.get('duration', '3 days')
        total_budget = inputs.get('total_budget', 2000)
        budget_category = inputs.get('budget_category', 'mid_range')
        
        # Parse duration to get number of days
        days = self._parse_duration(duration)
        
        # Get destination cost multiplier
        multiplier = self.destination_multipliers.get(destination, 1.0)
        
        # Calculate costs for each category
        daily_costs = {}
        total_estimated_cost = 0
        
        for category, costs in self.base_costs.items():
            base_cost = costs.get(budget_category, costs['mid_range'])
            adjusted_cost = base_cost * multiplier
            daily_costs[category] = round(adjusted_cost, 2)
            total_estimated_cost += adjusted_cost * days
        
        # Add flight costs (estimated)
        flight_cost = self._estimate_flight_cost(destination, budget_category)
        total_estimated_cost += flight_cost
        
        # Calculate budget analysis
        budget_difference = total_budget - total_estimated_cost
        budget_status = "within_budget" if budget_difference >= 0 else "over_budget"
        
        # Generate recommendations
        recommendations = self._generate_budget_recommendations(
            total_budget, total_estimated_cost, budget_category, days
        )
        
        return {
            "task_type": "trip_cost_calculation",
            "destination": destination,
            "duration": f"{days} days",
            "budget_category": budget_category,
            "total_budget": total_budget,
            "estimated_cost": round(total_estimated_cost, 2),
            "budget_difference": round(budget_difference, 2),
            "budget_status": budget_status,
            "daily_breakdown": daily_costs,
            "flight_cost": flight_cost,
            "cost_per_day": round(sum(daily_costs.values()), 2),
            "recommendations": recommendations,
            "currency": "USD",
            "calculation_date": datetime.now().isoformat()
        }
    
    def _handle_budget_breakdown(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Provide detailed budget breakdown and allocation suggestions."""
        total_budget = inputs.get('total_budget', 2000)
        destination = inputs.get('destination', 'Unknown')
        duration = inputs.get('duration', '3 days')
        
        days = self._parse_duration(duration)
        
        # Recommended budget allocation percentages
        allocation_percentages = {
            "accommodation": 0.35,
            "food": 0.25,
            "transportation": 0.20,
            "activities": 0.15,
            "emergency_fund": 0.05
        }
        
        # Calculate allocations
        allocations = {}
        for category, percentage in allocation_percentages.items():
            allocations[category] = round(total_budget * percentage, 2)
        
        # Daily spending limits
        daily_limits = {}
        for category in ["accommodation", "food", "transportation", "activities"]:
            if category in allocations:
                daily_limits[category] = round(allocations[category] / days, 2)
        
        # Spending tips
        tips = self._generate_spending_tips(destination, total_budget)
        
        return {
            "task_type": "budget_breakdown",
            "total_budget": total_budget,
            "destination": destination,
            "duration": f"{days} days",
            "budget_allocation": allocations,
            "daily_spending_limits": daily_limits,
            "spending_tips": tips,
            "recommended_apps": [
                "Trail Wallet - Travel expense tracker",
                "Splitwise - Group expense sharing",
                "XE Currency - Exchange rates"
            ],
            "currency": "USD"
        }
    
    def _handle_savings_planning(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Create a savings plan for the trip."""
        target_amount = inputs.get('total_budget', 2000)
        months_to_save = inputs.get('months_to_save', 6)
        current_savings = inputs.get('current_savings', 0)
        
        amount_needed = target_amount - current_savings
        monthly_savings_needed = amount_needed / months_to_save if months_to_save > 0 else amount_needed
        
        # Generate savings strategies
        strategies = [
            f"Save ${round(monthly_savings_needed/4, 2)} per week",
            f"Cut dining out expenses by ${round(monthly_savings_needed * 0.3, 2)} monthly",
            f"Reduce entertainment budget by ${round(monthly_savings_needed * 0.2, 2)} monthly",
            "Use cashback credit cards for regular purchases",
            "Sell unused items to boost savings"
        ]
        
        # Create monthly milestones
        milestones = []
        for month in range(1, months_to_save + 1):
            target = current_savings + (monthly_savings_needed * month)
            milestones.append({
                "month": month,
                "target_amount": round(target, 2),
                "monthly_save": round(monthly_savings_needed, 2)
            })
        
        return {
            "task_type": "savings_planning",
            "target_amount": target_amount,
            "current_savings": current_savings,
            "amount_needed": round(amount_needed, 2),
            "months_to_save": months_to_save,
            "monthly_savings_needed": round(monthly_savings_needed, 2),
            "weekly_savings_needed": round(monthly_savings_needed / 4, 2),
            "daily_savings_needed": round(monthly_savings_needed / 30, 2),
            "savings_strategies": strategies,
            "monthly_milestones": milestones,
            "completion_date": datetime.now().replace(month=datetime.now().month + months_to_save).strftime("%Y-%m-%d") if months_to_save <= 12 else "Future date"
        }
    
    def _handle_currency_conversion(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle currency conversion and exchange rate information."""
        amount = inputs.get('amount', 1000)
        from_currency = inputs.get('from_currency', 'USD')
        to_currency = inputs.get('to_currency', 'EUR')
        destination = inputs.get('destination', '')
        
        # Get exchange rates
        from_rate = self.exchange_rates.get(from_currency, 1.0)
        to_rate = self.exchange_rates.get(to_currency, 1.0)
        
        # Convert amount
        usd_amount = amount / from_rate
        converted_amount = usd_amount * to_rate
        
        # Generate currency tips
        tips = [
            "Use ATMs for better exchange rates than currency exchange counters",
            "Notify your bank before traveling to avoid card blocks",
            "Consider getting a travel credit card with no foreign transaction fees",
            "Keep some cash for small vendors and tips"
        ]
        
        return {
            "task_type": "currency_conversion",
            "original_amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "converted_amount": round(converted_amount, 2),
            "exchange_rate": round(to_rate / from_rate, 4),
            "destination": destination,
            "currency_tips": tips,
            "last_updated": datetime.now().isoformat()
        }
    
    def _parse_duration(self, duration: str) -> int:
        """Parse duration string to extract number of days."""
        try:
            # Extract numbers from duration string
            numbers = ''.join(filter(str.isdigit, duration))
            days = int(numbers) if numbers else 3
            
            # Adjust if it seems to be weeks or months
            if 'week' in duration.lower():
                days *= 7
            elif 'month' in duration.lower():
                days *= 30
                
            return max(1, days)  # Ensure at least 1 day
        except:
            return 3  # Default fallback
    
    def _estimate_flight_cost(self, destination: str, budget_category: str) -> float:
        """Estimate flight costs based on destination and budget category."""
        base_flight_costs = {
            "budget": 400,
            "mid_range": 700,
            "luxury": 1200
        }
        
        base_cost = base_flight_costs.get(budget_category, 700)
        multiplier = self.destination_multipliers.get(destination, 1.0)
        
        # Add some randomness for realism
        variation = random.uniform(0.8, 1.2)
        
        return round(base_cost * multiplier * variation, 2)
    
    def _generate_budget_recommendations(self, total_budget: float, estimated_cost: float, 
                                       budget_category: str, days: int) -> List[str]:
        """Generate personalized budget recommendations."""
        recommendations = []
        
        if estimated_cost > total_budget:
            overage = estimated_cost - total_budget
            recommendations.extend([
                f"Consider reducing trip duration by {max(1, int(overage / (estimated_cost / days)))} days",
                f"Look for budget accommodations to save ~${overage * 0.4:.0f}",
                "Book flights in advance for better deals",
                "Consider traveling during off-peak season"
            ])
        else:
            surplus = total_budget - estimated_cost
            recommendations.extend([
                f"You have ${surplus:.0f} extra budget for activities or upgrades",
                "Consider upgrading accommodation or dining experiences",
                "Budget for souvenirs and unexpected expenses",
                "Keep 10-15% as emergency fund"
            ])
        
        # General recommendations
        recommendations.extend([
            "Use travel reward credit cards for bookings",
            "Compare prices across multiple booking platforms",
            "Consider travel insurance for protection"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _generate_spending_tips(self, destination: str, budget: float) -> List[str]:
        """Generate destination-specific spending tips."""
        tips = [
            "Download offline maps to avoid roaming charges",
            "Eat at local restaurants instead of tourist areas",
            "Use public transportation instead of taxis",
            "Look for free walking tours and activities",
            "Book accommodations with kitchen facilities to save on meals"
        ]
        
        # Add destination-specific tips
        destination_tips = {
            "Paris": ["Visit museums on first Sunday mornings for free entry", "Buy groceries at Monoprix for better prices"],
            "London": ["Get an Oyster Card for cheaper tube travel", "Many museums have free admission"],
            "Tokyo": ["Use convenience stores for affordable meals", "Get a JR Pass for train travel"],
            "New York": ["Walk instead of taking taxis when possible", "Happy hour deals at restaurants"]
        }
        
        if destination in destination_tips:
            tips.extend(destination_tips[destination])
        
        return tips[:3]  # Return top 3 tips