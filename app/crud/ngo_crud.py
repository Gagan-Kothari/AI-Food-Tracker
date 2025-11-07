"""
NGO-related CRUD operations
"""
from typing import List, Dict
import math

# Mock NGO database - In production, this would be a real database
# Format: {city: [list of NGOs]}
MOCK_NGO_DATABASE = {
    "mumbai": [
        {
            "id": 1,
            "name": "Mumbai Food Bank",
            "address": "Andheri West, Mumbai, Maharashtra 400053",
            "contact": "+91 22 1234-5678",
            "description": "Helping families in need with fresh food donations across Mumbai",
            "latitude": 19.1364,
            "longitude": 72.8297,
        },
        {
            "id": 2,
            "name": "Community Kitchen Mumbai",
            "address": "Bandra East, Mumbai, Maharashtra 400051",
            "contact": "+91 22 2345-6789",
            "description": "Providing meals to homeless and low-income individuals",
            "latitude": 19.0596,
            "longitude": 72.8295,
        },
        {
            "id": 3,
            "name": "Mumbai Shelter Support",
            "address": "Powai, Mumbai, Maharashtra 400076",
            "contact": "+91 22 3456-7890",
            "description": "Supporting local shelters with food and supplies",
            "latitude": 19.1197,
            "longitude": 72.9050,
        },
        {
            "id": 4,
            "name": "Mumbai Hunger Relief",
            "address": "Vile Parle, Mumbai, Maharashtra 400056",
            "contact": "+91 22 4567-8901",
            "description": "Fighting hunger and food waste in Mumbai",
            "latitude": 19.0990,
            "longitude": 72.8423,
        },
    ],
    "delhi": [
        {
            "id": 5,
            "name": "Delhi Food Bank",
            "address": "Connaught Place, New Delhi, Delhi 110001",
            "contact": "+91 11 1234-5678",
            "description": "Helping families in need with fresh food donations across Delhi",
            "latitude": 28.6315,
            "longitude": 77.2167,
        },
        {
            "id": 6,
            "name": "Community Kitchen Delhi",
            "address": "Dwarka, New Delhi, Delhi 110075",
            "contact": "+91 11 2345-6789",
            "description": "Providing meals to homeless and low-income individuals",
            "latitude": 28.5928,
            "longitude": 77.0469,
        },
        {
            "id": 7,
            "name": "Delhi Shelter Support",
            "address": "Rohini, New Delhi, Delhi 110085",
            "contact": "+91 11 3456-7890",
            "description": "Supporting local shelters with food and supplies",
            "latitude": 28.7430,
            "longitude": 77.0867,
        },
        {
            "id": 8,
            "name": "Delhi Hunger Relief",
            "address": "Saket, New Delhi, Delhi 110017",
            "contact": "+91 11 4567-8901",
            "description": "Fighting hunger and food waste in Delhi",
            "latitude": 28.5245,
            "longitude": 77.2065,
        },
    ],
    "bangalore": [
        {
            "id": 9,
            "name": "Bangalore Food Bank",
            "address": "Koramangala, Bangalore, Karnataka 560095",
            "contact": "+91 80 1234-5678",
            "description": "Helping families in need with fresh food donations across Bangalore",
            "latitude": 12.9352,
            "longitude": 77.6245,
        },
        {
            "id": 10,
            "name": "Community Kitchen Bangalore",
            "address": "Indiranagar, Bangalore, Karnataka 560038",
            "contact": "+91 80 2345-6789",
            "description": "Providing meals to homeless and low-income individuals",
            "latitude": 12.9784,
            "longitude": 77.6408,
        },
        {
            "id": 11,
            "name": "Bangalore Shelter Support",
            "address": "Whitefield, Bangalore, Karnataka 560066",
            "contact": "+91 80 3456-7890",
            "description": "Supporting local shelters with food and supplies",
            "latitude": 12.9698,
            "longitude": 77.7499,
        },
        {
            "id": 12,
            "name": "Bangalore Hunger Relief",
            "address": "HSR Layout, Bangalore, Karnataka 560102",
            "contact": "+91 80 4567-8901",
            "description": "Fighting hunger and food waste in Bangalore",
            "latitude": 12.9120,
            "longitude": 77.6446,
        },
    ],
    "default": [
        {
            "id": 13,
            "name": "Food Bank Central",
            "address": "123 Main St, City",
            "contact": "+1 234-567-8900",
            "description": "Helping families in need with fresh food donations",
            "latitude": 0.0,
            "longitude": 0.0,
        },
        {
            "id": 14,
            "name": "Community Kitchen",
            "address": "456 Oak Ave, City",
            "contact": "+1 234-567-8901",
            "description": "Providing meals to homeless and low-income individuals",
            "latitude": 0.0,
            "longitude": 0.0,
        },
        {
            "id": 15,
            "name": "Shelter Support Network",
            "address": "789 Pine St, City",
            "contact": "+1 234-567-8902",
            "description": "Supporting local shelters with food and supplies",
            "latitude": 0.0,
            "longitude": 0.0,
        },
    ],
}


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def get_ngos_by_location(latitude: float, longitude: float, limit: int = 4) -> List[Dict]:
    """
    Get NGOs near a given location based on latitude and longitude.
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
        limit: Maximum number of NGOs to return (default: 4)
        
    Returns:
        List of NGO dictionaries sorted by distance
    """
    # Determine city based on coordinates (simplified - in production, use reverse geocoding)
    city = "default"
    
    # Mumbai coordinates (approximate)
    if 18.9 <= latitude <= 19.3 and 72.7 <= longitude <= 73.0:
        city = "mumbai"
    # Delhi coordinates (approximate)
    elif 28.4 <= latitude <= 28.9 and 77.0 <= longitude <= 77.4:
        city = "delhi"
    # Bangalore coordinates (approximate)
    elif 12.8 <= latitude <= 13.1 and 77.4 <= longitude <= 77.8:
        city = "bangalore"
    
    # Get NGOs for the city (or default)
    ngos = MOCK_NGO_DATABASE.get(city, MOCK_NGO_DATABASE["default"])
    
    # Calculate distance for each NGO and sort by distance
    ngos_with_distance = []
    for ngo in ngos:
        distance = calculate_distance(latitude, longitude, ngo["latitude"], ngo["longitude"])
        ngo_copy = ngo.copy()
        ngo_copy["distance_km"] = round(distance, 2)
        ngos_with_distance.append(ngo_copy)
    
    # Sort by distance (closest first)
    ngos_with_distance.sort(key=lambda x: x["distance_km"])
    
    # Return top N NGOs
    return ngos_with_distance[:limit]


def get_ngos_by_city(city: str, limit: int = 4) -> List[Dict]:
    """
    Get NGOs for a specific city.
    
    Args:
        city: City name (lowercase)
        limit: Maximum number of NGOs to return (default: 4)
        
    Returns:
        List of NGO dictionaries
    """
    city_lower = city.lower()
    ngos = MOCK_NGO_DATABASE.get(city_lower, MOCK_NGO_DATABASE["default"])
    
    # Add distance as 0 for city-based search (or calculate if needed)
    for ngo in ngos:
        ngo["distance_km"] = 0.0
    
    return ngos[:limit]

