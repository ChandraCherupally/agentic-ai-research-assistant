# =========================================================
# IMPORTS
# =========================================================
import logging
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

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

