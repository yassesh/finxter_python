from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
import os

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPAPI_API_KEY"] = os.getenv("SERPAPI_API_KEY")

llm = OpenAI(temperature=0)

tools = load_tools(["serpapi", "llm-math"],llm =llm,serpapi_api_key = os.getenv("SERPAPI_API_KEY"))

agent = initialize_agent(tools,llm,agent="zero-shot-react-description", verbose = True)

agent.run("who is mr. olympia 2022?")


