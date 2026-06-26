
import logging
import requests
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_tavily import TavilySearch


# =========================================================
# CREATE SEARCH TOOL
# =========================================================

def create_search_tool(logger: logging.Logger) -> TavilySearch:
    """
    Create Tavily Search Tool.
    """

    try:
        logger.info("Initializing Tavily Search Tool...")
        search_tool = TavilySearch(max_results=2)
        logger.info("Tavily Search Tool initialized successfully.")
        return search_tool

    except Exception:
        logger.exception("Failed to initialize Tavily Search Tool.")
        raise


# =========================================================
# WEATHER TOOL
# =========================================================

def create_weather_tool(weather_api_key: str, logger: logging.Logger):
    """
    Factory method that creates
    Weather Tool.
    """

    @tool
    def get_weather_data(city: str) -> str:
        """
        Fetch current weather for a city.
        """

        logger.info(f"Weather Tool Invoked | city={city}")

        try:
            url = (
                "https://api.weatherstack.com/current"
                f"?access_key={weather_api_key}"
                f"&query={city}"
            )

            logger.info("Calling WeatherStack API...")

            response = requests.get(url,timeout=10)
            response.raise_for_status()
            data = response.json()

            if "current" not in data:
                logger.warning(f"No weather data found for {city}")

                return (
                    f"Could not fetch "
                    f"weather information for {city}."
                )

            logger.info(f"Weather fetched successfully for {city}")
            return (
                f"City: {city}\n"
                f"Temperature: "
                f"{data['current']['temperature']}°C\n"
                f"Weather: "
                f"{data['current']['weather_descriptions'][0]}\n"
                f"Humidity: "
                f"{data['current']['humidity']}%"
            )

        except requests.exceptions.Timeout:
            logger.exception("Weather API Timeout")
            return ("Weather service timed out.")

        except requests.exceptions.RequestException:
            logger.exception("Weather API Request Failed")
            return ("Weather service is unavailable.")

        except Exception:
            logger.exception("Unexpected error while fetching weather.")
            return ("Unexpected weather service error.")

    logger.info("Weather Tool initialized successfully.")
    return get_weather_data

