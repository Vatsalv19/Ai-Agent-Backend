import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize LLMs (optional - can be done in function)
openai_llm = ChatOpenAI(model="gpt-4o-mini")
groq_llm = ChatGroq(model="llama3-70b-8192")

# Initialize search tool
search_tool = TavilySearchResults(max_results=5)

system_prompt = "Act as an AI chatbot who is smart and friendly"

def get_response_from_ai_agent(llm_id, query, allow_search, provider, system_prompt):
    """
    Function to get response from the AI agent.
    """
    # Select the appropriate LLM based on provider
    if provider == "groq":
        llm = ChatGroq(model=llm_id)
    elif provider == "openai":
        llm = ChatOpenAI(model=llm_id)
    else:
        raise ValueError("Provider must be 'groq' or 'openai'")
    
    # Set up tools based on allow_search flag
    tools = [TavilySearchResults(max_results=5)] if allow_search else []
    
    # Create the agent with the selected LLM
    agent = create_react_agent(
        model=llm,  # Use the selected LLM
        tools=tools  # Pass tools directly, not as nested list
    )
    
    # Create proper message format with system prompt
    messages = []
    if system_prompt:
        from langchain_core.messages import SystemMessage
        messages.append(SystemMessage(content=system_prompt))
    messages.append(HumanMessage(content=query))
    
    state = {"messages": messages}
    
    # Get response from agent
    response = agent.invoke(state)
    messages = response.get("messages", [])
    
    # Extract AI messages
    ai_messages = [msg.content for msg in messages if isinstance(msg, AIMessage)]
    
    # Return the last AI message, or empty string if none found
    return ai_messages[-1] if ai_messages else ""