"""
NGO-related CRUD operations
"""
from typing import List, Dict, Optional
import math
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Google Maps API key
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Mock NGO database - Fallback when location is denied or API fails
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


def get_ngos_from_nominatim(latitude: float, longitude: float, limit: int = 4) -> Optional[List[Dict]]:
    """
    Get NGOs from OpenStreetMap/Nominatim (FREE, no API key required).
    Uses both Overpass API and Nominatim search.
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
        limit: Maximum number of NGOs to return (default: 4)
        
    Returns:
        List of NGO dictionaries or None if API call fails
    """
    ngos = []
    
    try:
        # Method 1: Use Nominatim search API (free, no API key)
        # Search for NGOs, food banks, charities near the location
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        
        search_terms = [
            "food bank",
            "NGO",
            "charity",
            "shelter",
            "community kitchen"
        ]
        
        for term in search_terms:
            if len(ngos) >= limit * 2:
                break
                
            try:
                params = {
                    "q": term,
                    "format": "json",
                    "limit": 10,
                    "addressdetails": 1,
                    "extratags": 1,
                    "namedetails": 1,
                    "bounded": 1,
                    "viewbox": f"{longitude-1.8},{latitude+1.8},{longitude+1.8},{latitude-1.8}",  # ~200km box
                    "user-agent": "FoodTrackerApp/1.0"  # Required by Nominatim
                }
                
                response = requests.get(nominatim_url, params=params, timeout=15, headers={
                    "User-Agent": "FoodTrackerApp/1.0"
                })
                
                if response.status_code == 200:
                    results = response.json()
                    for place in results:
                        if len(ngos) >= limit * 2:
                            break
                            
                        place_lat = float(place.get('lat', latitude))
                        place_lon = float(place.get('lon', longitude))
                        distance = calculate_distance(latitude, longitude, place_lat, place_lon)
                        
                        # Only include if within 200km
                        if distance <= 200:
                            name = place.get('display_name', '').split(',')[0] or place.get('name', 'Unknown NGO')
                            address = place.get('display_name', 'Address not available')
                            contact = place.get('extratags', {}).get('phone') or place.get('extratags', {}).get('contact:phone', 'Contact not available')
                            
                            # Skip if we already have this place
                            if any(abs(n['latitude'] - place_lat) < 0.001 and abs(n['longitude'] - place_lon) < 0.001 for n in ngos):
                                continue
                            
                            ngo = {
                                "id": place.get('place_id', len(ngos) + 1),
                                "name": name,
                                "address": address,
                                "contact": contact,
                                "description": f"Community service organization. Helping the community with food donations.",
                                "latitude": place_lat,
                                "longitude": place_lon,
                                "distance_km": round(distance, 2),
                                "rating": None,
                                "place_id": str(place.get('place_id', ''))
                            }
                            ngos.append(ngo)
                            
                # Be respectful - Nominatim has rate limits
                import time
                time.sleep(1)  # 1 second delay between requests
                
            except Exception as e:
                print(f"DEBUG: Error in Nominatim search for '{term}': {str(e)}")
                continue
        
        # Method 2: Use Overpass API for more structured data
        if len(ngos) < limit:
            try:
                overpass_url = "http://overpass-api.de/api/interpreter"
                query = f'[out:json][timeout:25];(node["amenity"="food_bank"](around:200000,{latitude},{longitude});node["amenity"="shelter"](around:200000,{latitude},{longitude});node["amenity"="community_centre"](around:200000,{latitude},{longitude});way["amenity"="food_bank"](around:200000,{latitude},{longitude});way["amenity"="shelter"](around:200000,{latitude},{longitude});way["amenity"="community_centre"](around:200000,{latitude},{longitude}););out center meta;'
                
                response = requests.get(overpass_url, params={'data': query}, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    elements = data.get('elements', [])
                    
                    for element in elements:
                        if len(ngos) >= limit * 2:
                            break
                            
                        # Get coordinates
                        if 'lat' in element and 'lon' in element:
                            place_lat = element['lat']
                            place_lon = element['lon']
                        elif 'center' in element:
                            place_lat = element['center']['lat']
                            place_lon = element['center']['lon']
                        else:
                            continue
                        
                        distance = calculate_distance(latitude, longitude, place_lat, place_lon)
                        
                        # Only include if within 200km
                        if distance <= 200:
                            name = element.get('tags', {}).get('name', 'Unknown NGO')
                            address = element.get('tags', {}).get('addr:full') or \
                                     f"{element.get('tags', {}).get('addr:street', '')}, {element.get('tags', {}).get('addr:city', '')}"
                            contact = element.get('tags', {}).get('phone') or element.get('tags', {}).get('contact:phone', 'Contact not available')
                            
                            # Skip duplicates
                            if any(abs(n['latitude'] - place_lat) < 0.001 and abs(n['longitude'] - place_lon) < 0.001 for n in ngos):
                                continue
                            
                            ngo = {
                                "id": element.get('id', len(ngos) + 1),
                                "name": name,
                                "address": address or "Address not available",
                                "contact": contact,
                                "description": f"Community service organization. {element.get('tags', {}).get('description', 'Helping the community with food donations.')}",
                                "latitude": place_lat,
                                "longitude": place_lon,
                                "distance_km": round(distance, 2),
                                "rating": None,
                                "place_id": str(element.get('id', ''))
                            }
                            ngos.append(ngo)
            except Exception as e:
                print(f"DEBUG: Error in Overpass query: {str(e)}")
        
        if ngos:
            # Sort by distance and return top N
            ngos.sort(key=lambda x: x["distance_km"])
            print(f"DEBUG: Found {len(ngos)} NGOs from OpenStreetMap (within 200km)")
            return ngos[:limit]
        else:
            print("DEBUG: No NGOs found in OpenStreetMap")
            return None
            
    except Exception as e:
        print(f"DEBUG: Error calling OpenStreetMap API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def get_ngos_from_google_maps(latitude: float, longitude: float, limit: int = 4) -> Optional[List[Dict]]:
    """
    Get NGOs from Google Maps Places API near a given location.
    Uses Text Search API for larger radius (200km) since Nearby Search is limited to 50km.
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
        limit: Maximum number of NGOs to return (default: 4)
        
    Returns:
        List of NGO dictionaries or None if API call fails
    """
    if not GOOGLE_MAPS_API_KEY:
        print("DEBUG: Google Maps API key not configured, using fallback")
        return None
    
    try:
        # First try Nearby Search (up to 50km) for more accurate results
        url_nearby = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params_nearby = {
            "location": f"{latitude},{longitude}",
            "radius": 50000,  # 50km radius (maximum for Nearby Search)
            "type": "establishment",
            "keyword": "NGO food bank charity donation",
            "key": GOOGLE_MAPS_API_KEY
        }
        
        print(f"DEBUG: Searching for NGOs within 50km of ({latitude}, {longitude})")
        response_nearby = requests.get(url_nearby, params=params_nearby, timeout=10)
        
        ngos = []
        
        if response_nearby.status_code == 200:
            data_nearby = response_nearby.json()
            
            if data_nearby.get("status") == "OK" and data_nearby.get("results"):
                print(f"DEBUG: Found {len(data_nearby.get('results', []))} results from Nearby Search")
                for place in data_nearby.get("results", []):
                    place_id = place.get("place_id")
                    details = get_place_details(place_id) if place_id else {}
                    
                    place_lat = place.get("geometry", {}).get("location", {}).get("lat", latitude)
                    place_lng = place.get("geometry", {}).get("location", {}).get("lng", longitude)
                    distance = calculate_distance(latitude, longitude, place_lat, place_lng)
                    
                    # Only include if within 200km
                    if distance <= 200:
                        ngo = {
                            "id": place_id or len(ngos) + 1,
                            "name": place.get("name", "Unknown NGO"),
                            "address": place.get("vicinity") or details.get("formatted_address", "Address not available"),
                            "contact": details.get("formatted_phone_number") or details.get("international_phone_number", "Contact not available"),
                            "description": f"Located near you. {details.get('editorial_summary', {}).get('overview', 'Helping the community with food donations.')}",
                            "latitude": place_lat,
                            "longitude": place_lng,
                            "distance_km": round(distance, 2),
                            "rating": place.get("rating"),
                            "place_id": place_id
                        }
                        ngos.append(ngo)
        
        # If we don't have enough results, use Text Search for larger area (up to 200km)
        if len(ngos) < limit:
            print(f"DEBUG: Only found {len(ngos)} NGOs nearby, expanding search to 200km using Text Search")
            
            # Use Text Search API for broader search
            url_text = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            # Search terms for NGOs, food banks, charities
            search_queries = [
                "NGO food bank",
                "charity organization",
                "food donation center",
                "non-profit organization"
            ]
            
            for query in search_queries:
                if len(ngos) >= limit * 2:  # Get more than needed to filter by distance
                    break
                    
                params_text = {
                    "query": query,
                    "location": f"{latitude},{longitude}",
                    "radius": 200000,  # 200km in meters
                    "key": GOOGLE_MAPS_API_KEY
                }
                
                try:
                    response_text = requests.get(url_text, params=params_text, timeout=10)
                    if response_text.status_code == 200:
                        data_text = response_text.json()
                        if data_text.get("status") == "OK" and data_text.get("results"):
                            print(f"DEBUG: Found {len(data_text.get('results', []))} results for query: {query}")
                            for place in data_text.get("results", []):
                                place_id = place.get("place_id")
                                
                                # Skip if we already have this place
                                if any(n.get("place_id") == place_id for n in ngos):
                                    continue
                                
                                place_lat = place.get("geometry", {}).get("location", {}).get("lat", latitude)
                                place_lng = place.get("geometry", {}).get("location", {}).get("lng", longitude)
                                distance = calculate_distance(latitude, longitude, place_lat, place_lng)
                                
                                # Only include if within 200km
                                if distance <= 200:
                                    details = get_place_details(place_id) if place_id else {}
                                    ngo = {
                                        "id": place_id or len(ngos) + 1,
                                        "name": place.get("name", "Unknown NGO"),
                                        "address": place.get("formatted_address") or details.get("formatted_address", "Address not available"),
                                        "contact": details.get("formatted_phone_number") or details.get("international_phone_number", "Contact not available"),
                                        "description": f"Located near you. {details.get('editorial_summary', {}).get('overview', 'Helping the community with food donations.')}",
                                        "latitude": place_lat,
                                        "longitude": place_lng,
                                        "distance_km": round(distance, 2),
                                        "rating": place.get("rating"),
                                        "place_id": place_id
                                    }
                                    ngos.append(ngo)
                except Exception as e:
                    print(f"DEBUG: Error in Text Search for '{query}': {str(e)}")
                    continue
        
        if ngos:
            # Sort by distance and return top N
            ngos.sort(key=lambda x: x["distance_km"])
            print(f"DEBUG: Returning {min(len(ngos), limit)} NGOs (found {len(ngos)} total within 200km)")
            return ngos[:limit]
        else:
            print(f"DEBUG: No NGOs found within 200km")
            return None
            
    except Exception as e:
        print(f"DEBUG: Error calling Google Maps API: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def get_place_details(place_id: str) -> Dict:
    """
    Get detailed information about a place using Google Maps Places API.
    
    Args:
        place_id: Google Maps place ID
        
    Returns:
        Dictionary with place details
    """
    if not GOOGLE_MAPS_API_KEY or not place_id:
        return {}
    
    try:
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "formatted_address,formatted_phone_number,international_phone_number,editorial_summary",
            "key": GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK":
                return data.get("result", {})
        
        return {}
    except Exception as e:
        print(f"DEBUG: Error getting place details: {str(e)}")
        return {}


def detect_nearest_major_city(latitude: float, longitude: float) -> str:
    """
    Detect the nearest major city based on coordinates.
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
        
    Returns:
        City name (lowercase) or "default" if none found
    """
    # Top 100 Major Indian cities with approximate coordinates
    major_cities = {
        # Tier 1 Cities
        "mumbai": (19.0760, 72.8777),
        "delhi": (28.6139, 77.2090),
        "bengaluru": (12.9716, 77.5946),
        "hyderabad": (17.3850, 78.4867),
        "chennai": (13.0827, 80.2707),
        "kolkata": (22.5726, 88.3639),
        "pune": (18.5204, 73.8567),
        "ahmedabad": (23.0225, 72.5714),
        "jaipur": (26.9124, 75.7873),
        "surat": (21.1702, 72.8311),
        
        # Tier 2 Cities
        "lucknow": (26.8467, 80.9462),
        "kanpur": (26.4499, 80.3319),
        "nagpur": (21.1458, 79.0882),
        "indore": (22.7196, 75.8577),
        "thane": (19.2183, 72.9781),
        "bhopal": (23.2599, 77.4126),
        "visakhapatnam": (17.6868, 83.2185),
        "patna": (25.5941, 85.1376),
        "vadodara": (22.3072, 73.1812),
        "ghaziabad": (28.6692, 77.4538),
        
        "ludhiana": (30.9010, 75.8573),
        "agra": (27.1767, 78.0081),
        "nashik": (19.9975, 73.7898),
        "faridabad": (28.4089, 77.3178),
        "meerut": (28.9845, 77.7064),
        "rajkot": (22.3039, 70.8022),
        "varanasi": (25.3176, 82.9739),
        "srinagar": (34.0837, 74.7973),
        "amritsar": (31.6340, 74.8723),
        "aurangabad": (19.8762, 75.3433),
        
        "dhanbad": (23.7957, 86.4304),
        "amravati": (20.9374, 77.7796),
        "allahabad": (25.4358, 81.8463),
        "ranchi": (23.3441, 85.3096),
        "howrah": (22.5958, 88.2636),
        "jabalpur": (23.1815, 79.9864),
        "gwalior": (26.2183, 78.1828),
        "vijayawada": (16.5062, 80.6480),
        "jodhpur": (26.2389, 73.0243),
        "raipur": (21.2514, 81.6296),
        
        "kota": (25.2138, 75.8648),
        "guwahati": (26.1445, 91.7362),
        "chandigarh": (30.7333, 76.7794),
        "solapur": (17.6599, 75.9064),
        "hubli": (15.3647, 75.1240),
        "mysore": (12.2958, 76.6394),
        "tiruchirappalli": (10.7905, 78.7047),
        "bareilly": (28.3670, 79.4304),
        "moradabad": (28.8389, 78.7768),
        "gurgaon": (28.4089, 77.0868),
        
        "aligarh": (27.8974, 78.0880),
        "jalandhar": (31.3260, 75.5762),
        "bhubaneswar": (20.2961, 85.8245),
        "salem": (11.6643, 78.1460),
        "warangal": (18.0000, 79.5833),
        "guntur": (16.3067, 80.4365),
        "bhiwandi": (19.3000, 73.0667),
        "saharanpur": (29.9670, 77.5450),
        "gorakhpur": (26.7588, 83.3697),
        "bikaner": (28.0229, 73.3119),
        "noida": (28.5355, 77.3910),
        "jamshedpur": (22.8046, 86.2029),
        "bhilai": (21.2092, 81.4285),
        "cuttack": (20.4625, 85.8830),
        "firozabad": (27.1500, 78.3947),
        "kochi": (9.9312, 76.2673),
        "nellore": (14.4426, 79.9865),
        "bhavnagar": (21.7645, 72.1519),
        "dehradun": (30.3165, 78.0322),
        
        "durgapur": (23.5204, 87.3119),
        "asansol": (23.6889, 86.9661),
        "rourkela": (22.2604, 84.8536),
        "nanded": (19.1533, 77.3050),
        "kolhapur": (16.7050, 74.2433),
        "ajmer": (26.4499, 74.6399),
        "akola": (20.7000, 77.0000),
        "belgaum": (15.8497, 74.4977),
        "jamnagar": (22.4707, 70.0587),
        "udaipur": (24.5854, 73.7125),
        
        "mangalore": (12.9141, 74.8560),
        "kozhikode": (11.2588, 75.7804),
        "davangere": (14.4644, 75.9219),
        "kurnool": (15.8281, 78.0373),
        "rajahmundry": (17.0000, 81.7833),
        "bellary": (15.1394, 76.9214),
        "patiala": (30.3398, 76.3869),
        "shimla": (31.1048, 77.1734),
        "thrissur": (10.5276, 76.2144),
        
        "karnal": (29.6857, 76.9905),
        "panipat": (29.3909, 76.9695),
        "bathinda": (30.2070, 74.9455),
        "rohtak": (28.8955, 76.6066),
        "hisar": (29.1492, 75.7217),
        "sonipat": (28.9931, 77.0151),
        "panchkula": (30.6942, 76.8606),
        "ambala": (30.3782, 76.7767),
        "yamunanagar": (30.1290, 77.2883),
        
        "muzaffarnagar": (29.4709, 77.7033),
        "bijnor": (29.3722, 78.1364),
        "shahjahanpur": (27.8815, 79.9106),
        "rampur": (28.8073, 79.0262),
        "modinagar": (28.8283, 77.5792),
        "hapur": (28.7304, 77.7814),
        "bulandshahr": (28.4030, 77.8577),
        "mathura": (27.4924, 77.6737),
        "fatehpur": (25.9297, 80.8134),
        "unnao": (26.5473, 80.4878),
        
        "raebareli": (26.2309, 81.2332),
        "sultanpur": (26.2648, 82.0737),
        "faizabad": (26.7500, 82.1500),
        "barabanki": (26.9260, 81.1950),
        "sitapur": (27.5619, 80.6824),
        "hardoi": (27.3943, 80.1311),
        "lakhimpur": (27.9483, 80.7653),
        "pilibhit": (28.6310, 79.8044),
        "etawah": (26.7766, 79.0214),
        "coimbatore": (11.0168, 76.9558),
        
        "madurai": (9.9252, 78.1198),
        "tirunelveli": (8.7139, 77.7567),
        "tirupur": (11.1085, 77.3411),
        "erode": (11.3410, 77.7172),
        "vellore": (12.9165, 79.1325),
        "dindigul": (10.3629, 77.9750),
        "thanjavur": (10.7867, 79.1378),
        "tuticorin": (8.7642, 78.1348),
        "nagercoil": (8.1773, 77.4343),
        "karur": (10.9601, 78.0767),
        
        "hospet": (15.2695, 76.3871),
        "gadag": (15.4319, 75.6319),
        "bidar": (17.9104, 77.5199),
        "chitradurga": (14.2264, 76.4008),
        "kolar": (13.1355, 78.1326),
        "mandya": (12.5221, 76.8974),
        "hassan": (13.0033, 76.1004),
        "udupi": (13.3409, 74.7421),
        "chikmagalur": (13.3161, 75.7720),
        "shimoga": (13.9299, 75.5681),
        
        "tumkur": (13.3409, 77.1010),
        "chikkaballapur": (13.4350, 77.7275),
        "ramanagara": (12.7238, 77.2815),
        "chamrajnagar": (11.9271, 76.9430),
        "bagalkot": (16.1690, 75.6586),
        "bijapur": (16.8244, 75.7154),
        "gulbarga": (17.3297, 76.8343),
        "raichur": (16.2076, 77.3463),
        "koppal": (15.3547, 76.1544),
    }
    
    min_distance = float('inf')
    nearest_city = "default"
    
    for city_name, (city_lat, city_lon) in major_cities.items():
        distance = calculate_distance(latitude, longitude, city_lat, city_lon)
        if distance < min_distance:
            min_distance = distance
            nearest_city = city_name
    
    print(f"DEBUG: Nearest major city detected: {nearest_city} (distance: {min_distance:.2f} km)")
    return nearest_city


def get_ngos_by_location(latitude: float, longitude: float, limit: int = 4) -> List[Dict]:
    """
    Get NGOs near a given location based on latitude and longitude.
    First tries Google Maps API, then searches in nearest major city if no results.
    
    Args:
        latitude: User's latitude
        longitude: User's longitude
        limit: Maximum number of NGOs to return (default: 4)
        
    Returns:
        List of NGO dictionaries sorted by distance
    """
    # Check if Google Maps API key is configured
    if not GOOGLE_MAPS_API_KEY:
        print("DEBUG: ⚠️ Google Maps API key NOT configured!")
        print("DEBUG: To enable Google Maps search, add GOOGLE_MAPS_API_KEY to your environment variables")
        print("DEBUG: Falling back to city-based detection...")
    else:
        print(f"DEBUG: ✅ Google Maps API key found (first 10 chars: {GOOGLE_MAPS_API_KEY[:10]}...)")
    
    # Try OpenStreetMap/Nominatim first (FREE, no API key needed)
    print(f"DEBUG: Attempting OpenStreetMap search for ({latitude}, {longitude})")
    osm_ngos = get_ngos_from_nominatim(latitude, longitude, limit)
    if osm_ngos and len(osm_ngos) > 0:
        print(f"DEBUG: ✅ Found {len(osm_ngos)} NGOs from OpenStreetMap")
        return osm_ngos
    else:
        print("DEBUG: ❌ No NGOs found via OpenStreetMap")
    
    # Try Google Maps API (only if key is configured and OSM didn't find results)
    if GOOGLE_MAPS_API_KEY:
        print(f"DEBUG: Attempting Google Maps API search for ({latitude}, {longitude})")
        google_ngos = get_ngos_from_google_maps(latitude, longitude, limit)
        if google_ngos and len(google_ngos) > 0:
            print(f"DEBUG: ✅ Found {len(google_ngos)} NGOs from Google Maps")
            return google_ngos
        else:
            print("DEBUG: ❌ No NGOs found via Google Maps API search")
    else:
        print("DEBUG: ⏭️ Skipping Google Maps API search (no API key)")
    
    # If no results from Google Maps, detect nearest major city and search there
    print("DEBUG: Detecting nearest major city...")
    nearest_city = detect_nearest_major_city(latitude, longitude)
    
    # Try Nominatim search for the nearest city (FREE, no API key needed)
    if nearest_city != "default":
        print(f"DEBUG: Searching for NGOs in {nearest_city} using Nominatim (free)")
        city_ngos = search_ngos_in_city_nominatim(nearest_city, latitude, longitude, limit)
        if city_ngos and len(city_ngos) > 0:
            print(f"DEBUG: ✅ Found {len(city_ngos)} NGOs in {nearest_city} via Nominatim")
            return city_ngos
        else:
            print(f"DEBUG: ❌ No NGOs found in {nearest_city} via Nominatim")
    
    # Try Google Maps Text Search for the nearest city (only if key is configured and Nominatim failed)
    if nearest_city != "default" and GOOGLE_MAPS_API_KEY:
        print(f"DEBUG: Searching for NGOs in {nearest_city} using Google Maps Text Search")
        city_ngos = search_ngos_in_city_google_maps(nearest_city, latitude, longitude, limit)
        if city_ngos and len(city_ngos) > 0:
            print(f"DEBUG: ✅ Found {len(city_ngos)} NGOs in {nearest_city} via Google Maps")
            return city_ngos
        else:
            print(f"DEBUG: ❌ No NGOs found in {nearest_city} via Google Maps")
    
    # Fallback to static database for the nearest city
    print(f"DEBUG: ⚠️ Using fallback static NGO database for {nearest_city}")
    print(f"DEBUG: Note: Static database has limited cities. For real NGOs, configure GOOGLE_MAPS_API_KEY")
    print(f"DEBUG: Available cities in static DB: {list(MOCK_NGO_DATABASE.keys())}")
    
    # Get NGOs for the city (or default)
    # Map detected city to available static cities if needed
    city_mapping = {
        "chennai": "mumbai",  # Use Mumbai as fallback for Chennai
        "bengaluru": "bangalore",  # Map bengaluru to bangalore
        "trichy": "bangalore",
        "coimbatore": "bangalore",
        "madurai": "bangalore",
    }
    
    # Use mapped city if available, otherwise use detected city, otherwise default
    static_city = city_mapping.get(nearest_city, nearest_city)
    if static_city not in MOCK_NGO_DATABASE:
        static_city = "default"
        print(f"DEBUG: City '{nearest_city}' not in static DB, using 'default'")
    
    ngos = MOCK_NGO_DATABASE.get(static_city, MOCK_NGO_DATABASE["default"])
    print(f"DEBUG: Using static city: {static_city}, found {len(ngos)} NGOs")
    
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


def search_ngos_in_city_nominatim(city_name: str, user_lat: float, user_lon: float, limit: int = 4) -> Optional[List[Dict]]:
    """
    Search for NGOs in a specific city using Nominatim (FREE, no API key).
    
    Args:
        city_name: Name of the city to search in
        user_lat: User's latitude (for distance calculation)
        user_lon: User's longitude (for distance calculation)
        limit: Maximum number of NGOs to return
        
    Returns:
        List of NGO dictionaries or None if API call fails
    """
    try:
        # Capitalize city name for search
        city_display = city_name.capitalize()
        
        # Search queries for the city
        search_queries = [
            f"NGO {city_display}",
            f"food bank {city_display}",
            f"charity {city_display}",
            f"food donation {city_display}",
            f"non-profit {city_display}"
        ]
        
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        ngos = []
        
        for query in search_queries:
            if len(ngos) >= limit * 2:
                break
                
            try:
                params = {
                    "q": query,
                    "format": "json",
                    "limit": 10,
                    "addressdetails": 1,
                    "extratags": 1,
                    "user-agent": "FoodTrackerApp/1.0"
                }
                
                response = requests.get(nominatim_url, params=params, timeout=15, headers={
                    "User-Agent": "FoodTrackerApp/1.0"
                })
                
                if response.status_code == 200:
                    results = response.json()
                    for place in results:
                        if len(ngos) >= limit * 2:
                            break
                            
                        place_lat = float(place.get('lat', user_lat))
                        place_lon = float(place.get('lon', user_lon))
                        distance = calculate_distance(user_lat, user_lon, place_lat, place_lon)
                        
                        # Include NGOs within reasonable distance (up to 200km from user)
                        if distance <= 200:
                            name = place.get('display_name', '').split(',')[0] or place.get('name', 'Unknown NGO')
                            address = place.get('display_name', 'Address not available')
                            contact = place.get('extratags', {}).get('phone') or place.get('extratags', {}).get('contact:phone', 'Contact not available')
                            
                            # Skip duplicates
                            if any(abs(n['latitude'] - place_lat) < 0.001 and abs(n['longitude'] - place_lon) < 0.001 for n in ngos):
                                continue
                            
                            ngo = {
                                "id": place.get('place_id', len(ngos) + 1),
                                "name": name,
                                "address": address,
                                "contact": contact,
                                "description": f"Located in {city_display}. Helping the community with food donations.",
                                "latitude": place_lat,
                                "longitude": place_lon,
                                "distance_km": round(distance, 2),
                                "rating": None,
                                "place_id": str(place.get('place_id', ''))
                            }
                            ngos.append(ngo)
                
                # Be respectful - Nominatim has rate limits
                import time
                time.sleep(1)  # 1 second delay between requests
                
            except Exception as e:
                print(f"DEBUG: Error in Nominatim city search for '{query}': {str(e)}")
                continue
        
        if ngos:
            # Sort by distance and return top N
            ngos.sort(key=lambda x: x["distance_km"])
            print(f"DEBUG: Returning {min(len(ngos), limit)} NGOs from {city_display} via Nominatim (found {len(ngos)} total)")
            return ngos[:limit]
        else:
            return None
            
    except Exception as e:
        print(f"DEBUG: Error searching NGOs in city via Nominatim: {str(e)}")
        return None


def search_ngos_in_city_google_maps(city_name: str, user_lat: float, user_lon: float, limit: int = 4) -> Optional[List[Dict]]:
    """
    Search for NGOs in a specific city using Google Maps Text Search API.
    
    Args:
        city_name: Name of the city to search in
        user_lat: User's latitude (for distance calculation)
        user_lon: User's longitude (for distance calculation)
        limit: Maximum number of NGOs to return
        
    Returns:
        List of NGO dictionaries or None if API call fails
    """
    if not GOOGLE_MAPS_API_KEY:
        return None
    
    try:
        # Capitalize city name for search
        city_display = city_name.capitalize()
        
        # Search queries for the city
        search_queries = [
            f"NGO {city_display}",
            f"food bank {city_display}",
            f"charity {city_display}",
            f"food donation {city_display}",
            f"non-profit {city_display}"
        ]
        
        url_text = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        ngos = []
        
        for query in search_queries:
            if len(ngos) >= limit * 2:
                break
                
            params_text = {
                "query": query,
                "key": GOOGLE_MAPS_API_KEY
            }
            
            try:
                response_text = requests.get(url_text, params=params_text, timeout=10)
                if response_text.status_code == 200:
                    data_text = response_text.json()
                    if data_text.get("status") == "OK" and data_text.get("results"):
                        print(f"DEBUG: Found {len(data_text.get('results', []))} results for query: {query}")
                        for place in data_text.get("results", []):
                            place_id = place.get("place_id")
                            
                            # Skip if we already have this place
                            if any(n.get("place_id") == place_id for n in ngos):
                                continue
                            
                            place_lat = place.get("geometry", {}).get("location", {}).get("lat", user_lat)
                            place_lon = place.get("geometry", {}).get("location", {}).get("lng", user_lon)
                            distance = calculate_distance(user_lat, user_lon, place_lat, place_lon)
                            
                            # Include NGOs within reasonable distance (up to 200km from user)
                            if distance <= 200:
                                details = get_place_details(place_id) if place_id else {}
                                ngo = {
                                    "id": place_id or len(ngos) + 1,
                                    "name": place.get("name", "Unknown NGO"),
                                    "address": place.get("formatted_address") or details.get("formatted_address", "Address not available"),
                                    "contact": details.get("formatted_phone_number") or details.get("international_phone_number", "Contact not available"),
                                    "description": f"Located in {city_display}. {details.get('editorial_summary', {}).get('overview', 'Helping the community with food donations.')}",
                                    "latitude": place_lat,
                                    "longitude": place_lon,
                                    "distance_km": round(distance, 2),
                                    "rating": place.get("rating"),
                                    "place_id": place_id
                                }
                                ngos.append(ngo)
            except Exception as e:
                print(f"DEBUG: Error in Text Search for '{query}': {str(e)}")
                continue
        
        if ngos:
            # Sort by distance and return top N
            ngos.sort(key=lambda x: x["distance_km"])
            print(f"DEBUG: Returning {min(len(ngos), limit)} NGOs from {city_display} (found {len(ngos)} total)")
            return ngos[:limit]
        else:
            return None
            
    except Exception as e:
        print(f"DEBUG: Error searching NGOs in city: {str(e)}")
        return None


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

