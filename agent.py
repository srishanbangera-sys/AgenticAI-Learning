# -----------------------------------------------------------------------------
# Module Imports
# -----------------------------------------------------------------------------
import os  # Provides access to operating system functionalities and environment variables
from dotenv import load_dotenv  # Reads key-value pairs from a .env file and sets them as environment variables
# pyrefly: ignore [missing-import]
from langchain_core.tools import tool  # Decorator to convert standard Python functions into LangChain tools
# pyrefly: ignore [missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI  # LangChain integration class for Google Gemini chat models
# pyrefly: ignore [missing-import]
from langgraph.prebuilt import create_react_agent  # Helper function from LangGraph to construct a prebuilt ReAct agent workflow

# -----------------------------------------------------------------------------
# Environment Configuration
# -----------------------------------------------------------------------------
# Load environment variables from the local .env file into os.environ
load_dotenv()

# -----------------------------------------------------------------------------
# STEP 1: INITIALIZE THE BRAIN (Reasoning Model)
# -----------------------------------------------------------------------------
# Retrieve the Gemini API key from the environment variables
api_key = os.environ.get("GEMINI_API_KEY")

# Validate that the API key exists; raise an explicit error if missing
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is missing. Please set it in your environment or in a .env file.")

# Initialize the Gemini Chat Model
# - model: The specific Gemini model variant to use
# - google_api_key: Authentication key for Google AI Studio / Gemini API
# - temperature: Set to 0.0 for deterministic, factual, and consistent reasoning/tool selection
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0.0
)

# -----------------------------------------------------------------------------
# STEP 2: CREATE THE HANDS (Tools)
# -----------------------------------------------------------------------------
@tool  # Registers this function as a tool accessible to LLM agent
def calculate_math(expression: str) -> str:
    """Evaluates an exact mathematical expression safely using Python.
    
    Args:
        expression: A valid mathematical string expression, e.g. '(45000 * 1.08) ** 5'
    """
    try:
        # Evaluate mathematical string safely by stripping built-in functions to prevent arbitrary code execution
        result = eval(expression, {"__builtins__": None}, {})
        # Convert numeric result to string so the LLM can interpret it
        return str(result)
    except Exception as e:
        # Catch and return any calculation syntax errors to let the model recover gracefully
        return f"Calculation Error: {str(e)}"

@tool  # Registers this function as a tool accessible to LLM agent
def check_server_status(server_name: str) -> str:
    """Queries real-time infrastructure metrics for a given server name.
    
    Args:
        server_name: The identifier of the server (e.g., 'prod-db', 'auth-service')
    """
    # Simulated database storing status info for different servers
    mock_database = {
        "prod-db": "CPU: 94% [CRITICAL - Out of Memory Risk]",
        "auth-service": "CPU: 12% [HEALTHY]",
        "payment-gateway": "CPU: 45% [HEALTHY]"
    }
    # Look up the server name in lowercase; return fallback message if not found
    return mock_database.get(server_name.lower(), f"Server '{server_name}' not found in registry.")

# -----------------------------------------------------------------------------
# STEP 3: ASSEMBLE THE AGENT (The Orchestration Loop)
# -----------------------------------------------------------------------------
# Combine our defined tools into a list to provide to the agent
tools = [calculate_math, check_server_status]

# Create the ReAct (Reasoning + Acting) Agent graph
# - model: The LLM that acts as the agent's brain
# - tools: The list of executable functions the agent can call
# - prompt: System prompt defining the role, boundaries, and instructions for the agent
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt="You are an autonomous DevOps assistant. Use tools for any calculations and server lookups."
)

# -----------------------------------------------------------------------------
# STEP 4: RUN AND EXECUTE A MULTI-STEP GOAL
# -----------------------------------------------------------------------------
def format_output(content) -> str:
    """Formats the final response content from the agent into a readable string."""
    # If content is already a plain string, return directly
    if isinstance(content, str):
        return content
    # If content is a list of blocks/parts (e.g., Gemini multimodal or chunk structures), extract text fields
    if isinstance(content, list):
        text_parts = [item.get("text", "") for item in content if isinstance(item, dict) and "text" in item]
        return "\n".join(text_parts) if text_parts else str(content)
    # Fallback for any other data type
    return str(content)

# Main entry point when executing this script directly
if __name__ == "__main__":
    # Define the complex multi-step prompt that requires tool use and chaining
    goal = "Check the health of prod-db. Then calculate what 94% of 128 GB RAM is to see how much memory is consumed."
    print(f"Goal: {goal}\n")
    
    # Run the agent workflow by passing the user's initial message
    result = agent.invoke({"messages": [("user", goal)]})
    
    # Print header for clarity
    print("\n--- FINAL AGENT OUTPUT ---")
    # Extract and format the last message content from the agent's conversation history
    print(format_output(result["messages"][-1].content))
