import requests
import time

# Map your customer locations to latitude and longitude
location_to_coords = {
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
    # Add all other locations from your 'customers' table here
}

def get_historical_weather(latitude, longitude, year, month):
    """
    Fetches historical weather data for a given location and time from Open-Meteo.
    Returns average temperature and total precipitation.
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": f"{year}-{month:02d}-01",
        "end_date": f"{year}-{month:02d}-28",
        "daily": ["temperature_2m_mean", "precipitation_sum"],
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        avg_temp = data['daily']['temperature_2m_mean'][0]
        total_precip = data['daily']['precipitation_sum'][0]
        return avg_temp, total_precip
    except Exception as e:
        print(f"Weather API error for {latitude},{longitude} {year}-{month}: {e}")
        return None, None

def get_weather_for_location(location_name, year, month):
    """Main function to get weather for a named location."""
    coords = location_to_coords.get(location_name)
    if not coords:
        print(f"No coordinates found for location: {location_name}")
        return None, None
    lat, lon = coords
    return get_historical_weather(lat, lon, year, month)