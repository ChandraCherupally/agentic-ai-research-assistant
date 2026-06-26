"""
===========================================================
Production Grade LangChain Agent
-----------------------------------------------------------
Sections
1. Imports, 2. Constants, 3. Logging Configuration, 4. Environment Loading, 
5. Tavily Search Tool, 6. Weather Tool 7. create_llm, 8. create_langchain_agent, 9.run_agent
===========================================================
"""

# =========================================================
# IMPORTS
# =========================================================
from src import (
    setup_logging,
    load_environment,
    create_llm,
    create_langchain_agent,
    run_agent,
    create_search_tool,
    create_weather_tool,
)

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