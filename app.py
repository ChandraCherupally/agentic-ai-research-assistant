import streamlit as st
from src import (
    setup_logging,
    load_environment,
    create_llm,
    create_langchain_agent,
    create_search_tool,
    create_weather_tool,
)
# -----------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------------------------------
# LOAD AGENT ONLY ONCE
# -----------------------------------------------------

@st.cache_resource
def load_agent():

    logger = setup_logging()
    env = load_environment(logger)
    llm = create_llm(api_key=env["gemini"],logger=logger)

    search_tool = create_search_tool(logger)
    weather_tool = create_weather_tool(weather_api_key=env["weather"],logger=logger)

    tools = [search_tool, weather_tool]

    agent = create_langchain_agent(llm, tools, logger)
    return agent, logger

agent, logger = load_agent()

# -----------------------------------------------------
# TITLE
# -----------------------------------------------------

st.title("🤖 AI Research Agent")
st.markdown(
"""
This AI Agent can:

- 🌍 Search the web
- 🌦️ Get current weather
- 🧠 Reason before answering
"""
)

# -----------------------------------------------------
# CHAT HISTORY
# -----------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------
# DISPLAY HISTORY
# -----------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# -----------------------------------------------------
# CHAT INPUT
# -----------------------------------------------------

prompt = st.chat_input(
    "Ask me anything..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.sidebar:
        st.title("⚙️ Settings")
        st.success("Gemini 2.5 Flash")
        st.success("Tavily Search")
        st.success("WeatherStack")
        st.divider()
        if st.button("Clear Chat"):
            st.session_state.messages=[]
            st.rerun()        

    with st.chat_message("assistant"):
        with st.spinner("🤖 Thinking and using tools..."):
            try:
                logger.info(f"User Query : {prompt}")
                response = agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    }
                )

                answer = response["messages"][-1].content
                logger.info(answer)
                st.markdown(answer)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

            except Exception as e:

                logger.exception(e)

                st.error(
                            """
                            Something went wrong.
                            Please check:
                            • Internet connection
                            • API Keys
                            • Weather API
                            • Tavily API
                            """
                            )


