from typing import Dict, Any
import requests

CITIES = {
    "jakarta": {"latitude": -6.2088, "longitude": 106.8456, "name": "Jakarta"},
    "bandung": {"latitude": -6.9175, "longitude": 107.6191, "name": "Bandung"},
    "surabaya": {"latitude": -7.2575, "longitude": 112.7521, "name": "Surabaya"},
    "yogyakarta": {"latitude": -7.7956, "longitude": 110.3695, "name": "Yogyakarta"},
    "denpasar": {"latitude": -8.6705, "longitude": 115.2126, "name": "Denpasar"},
}

def _interpret_wmo_code(code: int) -> str:
    if code == 0:
        return "cerah"
    elif code in [1, 2, 3]:
        return "berawan"
    elif code in [45, 48]:
        return "berkabut"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "hujan"
    elif code in [95, 96, 99]:
        return "hujan petir"
    return "berawan"

def get_weather(city: str = "Jakarta") -> Dict[str, Any]:
    """Fetch current weather data for a given Indonesian city using the Open-Meteo API.
    
    Args:
        city: The city name (e.g., 'Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta', 'Denpasar'). Defaults to 'Jakarta'.
        
    Returns:
        Dictionary with temperature, apparent temperature, precipitation, condition, and today's max temperature.
    """
    city_key = city.strip().lower()
    city_info = CITIES.get(city_key, CITIES["jakarta"])
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": city_info["latitude"],
        "longitude": city_info["longitude"],
        "current": ["temperature_2m", "apparent_temperature", "precipitation", "weather_code"],
        "daily": ["temperature_2m_max"],
        "timezone": "Asia/Jakarta"
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        temp = current.get("temperature_2m")
        apparent_temp = current.get("apparent_temperature")
        precip = current.get("precipitation", 0.0)
        wmo_code = current.get("weather_code", 0)
        condition = _interpret_wmo_code(wmo_code)
        
        daily_max_list = daily.get("temperature_2m_max", [])
        max_temp = daily_max_list[0] if daily_max_list else temp

        return {
            "status": "success",
            "city": city_info["name"],
            "temperature_celsius": temp,
            "apparent_temperature_celsius": apparent_temp,
            "precipitation_mm": precip,
            "condition": condition,
            "max_temperature_celsius": max_temp
        }
    except requests.RequestException as e:
        return {
            "status": "error",
            "city": city_info["name"],
            "message": f"Unable to fetch weather data: {str(e)}"
        }
