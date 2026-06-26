# =========================================================
# IMPORTS
# =========================================================

import os
import logging
from pathlib import Path
import certifi
from dotenv import load_dotenv

# =========================================================
# PROJECT CONSTANTS
# =========================================================

APP_NAME = "LangChain-Agent"
BASE_DIR = Path(__file__).parent.parent
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

