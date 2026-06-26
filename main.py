"""
===========================================================
Production Grade LangChain Agent
Part 1
-----------------------------------------------------------
Sections
1. Imports
2. Constants
3. Logging Configuration
4. Environment Loading
5. Tavily Search Tool
6. Weather Tool
===========================================================
"""

# =========================================================
# IMPORTS
# =========================================================

import os
import logging
from pathlib import Path
import certifi
import requests
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent


# =========================================================
# PROJECT CONSTANTS
# =========================================================

APP_NAME = "LangChain-Agent"
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"


# =========================================================
# LOGGING CONFIGURATION
# =========================================================

def setup_logging() -> logging.Logger:
    """
    Configure application logging.

    Creates:
        logs/
            app.log

    Returns
    -------
    logging.Logger
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,

        format=("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),

        handlers=[
            logging.FileHandler(LOG_FILE,encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(APP_NAME)
    logger.info("=" * 70)
    logger.info("Application Started")
    logger.info("=" * 70)
    return logger


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

def load_environment(logger: logging.Logger) -> dict:
    """
    Load environment variables.

    Returns
    -------
    dict
        Dictionary containing all API keys.
    """

    try:

        logger.info("Loading environment variables...")
        os.environ["SSL_CERT_FILE"] = certifi.where()

        load_dotenv()
        gemini_key = os.getenv("GEMINI_API_KEY")
        tavily_key = os.getenv("TAVILY_API_KEY")
        weather_key = os.getenv("WEATHERSTACK_API_KEY")

        if not gemini_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        if not tavily_key:
            raise ValueError("TAVILY_API_KEY is missing.")

        if not weather_key:
            raise ValueError("WEATHERSTACK_API_KEY is missing.")

        logger.info("Environment variables loaded successfully.")

        return {"gemini": gemini_key, "tavily": tavily_key, "weather": weather_key}

    except Exception as e:
        logger.exception("Failed to load environment variables.")
        raise f"Failed to load {str(e)}"


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


# =========================================================
# CREATE LLM
# =========================================================

def create_llm(api_key: str, logger: logging.Logger) -> ChatOpenAI:
    """
    Create Gemini LLM.
    """

    try:
        logger.info("Initializing Gemini LLM...")
        llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            model="gemini-2.5-flash",
            temperature=0)
        logger.info("Gemini initialized successfully.")
        return llm

    except Exception:
        logger.exception("Failed to initialize Gemini.")
        raise


# =========================================================
# CREATE LANGCHAIN AGENT
# =========================================================

def create_langchain_agent(llm: ChatOpenAI, tools: list, logger: logging.Logger):
    """
    Create LangChain Agent.
    """

    try:
        logger.info("Creating LangChain Agent...")
        agent = create_agent(model=llm, tools=tools,
                            system_prompt="""
                            You are a helpful AI assistant.

                            Use tools whenever required.

                            Always provide concise and accurate answers.

                            If weather is requested,
                            always use the Weather Tool.

                            If current information is requested,
                            always use Tavily Search.
                            """
                        )

        logger.info("LangChain Agent created successfully.")

        return agent

    except Exception:
        logger.exception("Agent creation failed.")
        raise


# =========================================================
# RUN AGENT
# =========================================================

def run_agent(agent, query: str, logger: logging.Logger):
    """
    Execute user query.
    """

    try:
        logger.info("=" * 60)
        logger.info("User Query : %s", query)
        logger.info("=" * 60)
        response = agent.invoke({
                "messages": [
                    {
                        "role": "user",
                        "content": query
                    }
                ]
            })

        answer = response["messages"][-1].content
        logger.info("Agent execution completed.")
        logger.info("-" * 60)
        logger.info("FINAL RESPONSE")
        logger.info("-" * 60)
        logger.info(answer)
        return answer

    except Exception:
        logger.exception("Agent execution failed.")
        raise


# =========================================================
# MAIN
# =========================================================

def main():

    logger = setup_logging()

    try:

        # ------------------------------------------
        # Load Environment
        # ------------------------------------------
        env = load_environment(logger)

        # ------------------------------------------
        # Create LLM
        # ------------------------------------------
        llm = create_llm(api_key=env["gemini"], logger=logger)

        # ------------------------------------------
        # Create Tools
        # ------------------------------------------

        search_tool = create_search_tool(logger)
        weather_tool = create_weather_tool(weather_api_key=env["weather"], logger=logger)
        tools = [search_tool, weather_tool]
        logger.info("Registered %d tools.", len(tools))

        # ------------------------------------------
        # Create Agent
        # ------------------------------------------
        agent = create_langchain_agent(llm,tools,logger)

        # ------------------------------------------
        # User Query
        # ------------------------------------------

        query = (
            "Find the capital of Telangana "
            "and then find its current weather."
        )

        answer = run_agent(agent, query, logger)

        print("\n")
        print("=" * 70)
        print("FINAL OUTPUT")
        print("=" * 70)
        print(answer)
        print("=" * 70)

    except Exception:
        logger.exception("Application terminated unexpectedly.")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()