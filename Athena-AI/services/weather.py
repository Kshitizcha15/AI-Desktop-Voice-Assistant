import requests
from config import OPENWEATHER_API_KEY

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city):
    """
    Fetches current weather for a given city name using OpenWeatherMap.
    Returns a natural sentence describing the weather, or an error message
    if the city isn't found or the API call fails.
    """
    if not city:
        return "I need a city name to check the weather. Try 'weather in London'."

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"  # Celsius; change to "imperial" for Fahrenheit
    }

    try:
        response = requests.get(WEATHER_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        temp = round(data["main"]["temp"])
        feels_like = round(data["main"]["feels_like"])
        description = data["weather"][0]["description"]
        city_name = data["name"]

        return (
            f"It's currently {temp} degrees in {city_name}, "
            f"feels like {feels_like} degrees, with {description}."
        )

    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            return f"I couldn't find a city called {city}. Please check the spelling."
        elif response.status_code == 401:
            return "The weather service isn't set up correctly — check the API key."
        else:
            return "I couldn't reach the weather service right now."
    except requests.exceptions.RequestException:
        return "I couldn't reach the weather service right now. Check your internet connection."