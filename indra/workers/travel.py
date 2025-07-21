"""Travel Worker - Handles travel-related tasks with stubbed data."""

import random
from typing import Dict, Any
from datetime import datetime, timedelta
from ..base_worker import BaseWorker, register_worker


@register_worker("travel")
class TravelWorker(BaseWorker):
    """Travel worker that handles travel-related tasks."""
    
    def __init__(self, worker_name: str = "travel", results_dir: str = "results"):
        """Initialize the travel worker."""
        super().__init__(worker_name, results_dir)
        
        # Stubbed data for demonstrations
        self.cities = {
            "Paris": {"country": "France", "timezone": "CET", "currency": "EUR"},
            "London": {"country": "UK", "timezone": "GMT", "currency": "GBP"},
            "Tokyo": {"country": "Japan", "timezone": "JST", "currency": "JPY"},
            "New York": {"country": "USA", "timezone": "EST", "currency": "USD"},
            "Sydney": {"country": "Australia", "timezone": "AEST", "currency": "AUD"},
            "Dubai": {"country": "UAE", "timezone": "GST", "currency": "AED"},
            "Singapore": {"country": "Singapore", "timezone": "SGT", "currency": "SGD"},
            "Barcelona": {"country": "Spain", "timezone": "CET", "currency": "EUR"},
        }
        
        self.airlines = ["Air France", "British Airways", "Emirates", "Singapore Airlines", "Lufthansa", "Delta", "United"]
        self.hotel_chains = ["Hilton", "Marriott", "Hyatt", "InterContinental", "Radisson", "Sheraton", "Westin"]
    
    def execute(self, **inputs) -> Dict[str, Any]:
        """Execute travel-related tasks."""
        task_type = inputs.get('task', 'general_travel_planning')
        destination = inputs.get('destination', 'Paris')
        duration = inputs.get('duration', '3 days')
        
        # Handle empty or None destination
        if not destination or not destination.strip():
            destination = 'Paris'  # Default fallback
        
        # Route to specific task handlers
        if task_type in ['find_flights', 'flight_search']:
            return self._handle_flight_search(inputs)
        elif task_type in ['find_hotels', 'hotel_search']:
            return self._handle_hotel_search(inputs)
        elif task_type in ['travel_planning', 'plan_itinerary']:
            return self._handle_travel_planning(inputs)
        else:
            # General travel task - provide simple stubbed data
            return {
                "task_type": task_type,
                "destination": destination,
                "duration": duration,
                "flights": [
                    {"airline": "Air France", "price": 650, "duration": "8h 30m"},
                    {"airline": "British Airways", "price": 720, "duration": "9h 15m"}
                ],
                "hotels": [
                    {"name": "Hotel Paris", "price": 150, "rating": 4.2},
                    {"name": "Grand Hotel", "price": 200, "rating": 4.5}
                ],
                "activities": [
                    "Visit Eiffel Tower",
                    "Explore Louvre Museum", 
                    "Walk along Seine River"
                ],
                "estimated_cost": 1200
            }
    
    def _handle_flight_search(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flight search requests."""
        destination = inputs.get('destination', 'Paris')
        departure_city = inputs.get('departure_city', 'Current Location')
        duration = inputs.get('duration', '3 days')
        
        # Generate stubbed flight options
        flights = []
        for i in range(3):  # Generate 3 flight options
            airline = random.choice(self.airlines)
            price = random.randint(300, 1200)
            departure_time = datetime.now() + timedelta(days=random.randint(1, 30))
            
            flights.append({
                "airline": airline,
                "flight_number": f"{airline[:2].upper()}{random.randint(100, 999)}",
                "departure_city": departure_city,
                "destination": destination,
                "departure_time": departure_time.strftime("%Y-%m-%d %H:%M"),
                "duration": f"{random.randint(2, 12)}h {random.randint(0, 59)}m",
                "price": price,
                "currency": "USD",
                "stops": random.choice([0, 1, 2]),
                "class": random.choice(["Economy", "Premium Economy", "Business"])
            })
        
        # Sort by price
        flights.sort(key=lambda x: x['price'])
        
        return {
            "task_type": "flight_search",
            "destination": destination,
            "departure_city": departure_city,
            "search_date": datetime.now().isoformat(),
            "flights": flights,
            "recommendation": f"Best value flight: {flights[0]['airline']} {flights[0]['flight_number']} for ${flights[0]['price']}",
            "total_options": len(flights)
        }
    
    def _handle_hotel_search(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle hotel search requests."""
        destination = inputs.get('destination', 'Paris')
        duration = inputs.get('duration', '3 days')
        budget_range = inputs.get('budget_range', 'mid-range')
        
        # Parse duration to get number of nights
        nights = 3  # default
        if duration and 'day' in duration.lower():
            try:
                nights = int(''.join(filter(str.isdigit, duration)))
                if nights <= 0:
                    nights = 3
            except (ValueError, TypeError):
                nights = 3
        
        # Generate price range based on budget
        price_ranges = {
            'budget': (50, 120),
            'mid-range': (120, 300),
            'luxury': (300, 800)
        }
        price_min, price_max = price_ranges.get(budget_range, price_ranges['mid-range'])
        
        # Generate stubbed hotel options
        hotels = []
        for i in range(4):  # Generate 4 hotel options
            chain = random.choice(self.hotel_chains)
            price_per_night = random.randint(price_min, price_max)
            
            hotels.append({
                "name": f"{chain} {destination}",
                "chain": chain,
                "rating": round(random.uniform(3.5, 5.0), 1),
                "price_per_night": price_per_night,
                "total_price": price_per_night * nights,
                "currency": "USD",
                "location": f"{destination} City Center",
                "amenities": random.sample([
                    "Free WiFi", "Pool", "Gym", "Spa", "Restaurant", 
                    "Room Service", "Business Center", "Parking", "Airport Shuttle"
                ], k=random.randint(3, 6)),
                "distance_to_center": f"{random.uniform(0.1, 5.0):.1f} km"
            })
        
        # Sort by rating
        hotels.sort(key=lambda x: x['rating'], reverse=True)
        
        return {
            "task_type": "hotel_search",
            "destination": destination,
            "duration": duration,
            "nights": nights,
            "budget_range": budget_range,
            "search_date": datetime.now().isoformat(),
            "hotels": hotels,
            "recommendation": f"Top rated: {hotels[0]['name']} ({hotels[0]['rating']} stars) for ${hotels[0]['price_per_night']}/night",
            "total_options": len(hotels)
        }
    
    def _handle_travel_planning(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Handle comprehensive travel planning requests."""
        destination = inputs.get('destination', 'Paris')
        duration = inputs.get('duration', '3 days')
        
        # Get city information
        city_info = self.cities.get(destination, {
            "country": "Unknown",
            "timezone": "UTC",
            "currency": "USD"
        })
        
        # Generate itinerary suggestions
        activities = [
            "Visit famous landmarks and monuments",
            "Explore local museums and galleries",
            "Take a guided city walking tour",
            "Experience local cuisine and restaurants",
            "Visit traditional markets and shopping areas",
            "Enjoy parks and outdoor spaces",
            "Take day trips to nearby attractions",
            "Experience local nightlife and entertainment"
        ]
        
        # Generate weather forecast (stubbed)
        weather_conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Clear"]
        weather = []
        for i in range(7):  # 7-day forecast
            date = datetime.now() + timedelta(days=i)
            weather.append({
                "date": date.strftime("%Y-%m-%d"),
                "condition": random.choice(weather_conditions),
                "high": random.randint(15, 30),
                "low": random.randint(5, 20),
                "humidity": random.randint(40, 80)
            })
        
        return {
            "task_type": "travel_planning",
            "destination": destination,
            "duration": duration,
            "city_info": city_info,
            "suggested_activities": random.sample(activities, k=min(5, len(activities))),
            "weather_forecast": weather[:5],  # 5-day forecast
            "local_tips": [
                f"Best time to visit {destination} is during spring and fall",
                f"Local currency is {city_info['currency']}",
                f"Time zone is {city_info['timezone']}",
                "Book accommodations in advance for better rates",
                "Try local transportation for authentic experience"
            ],
            "estimated_daily_budget": {
                "budget": "$50-80",
                "mid_range": "$80-150", 
                "luxury": "$150-300"
            }
        }