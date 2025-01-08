import streamlit as st
from langchain import OpenAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.tools import PythonREPLTool

def return_agent():
	"""
	Initialize and return a LangChain-based agent with Python REPL tool.
	Configures Azure OpenAI as the language model backend.
	"""
	# API config (Azure OpenAI integration)
	openai_api_key = st.secrets['AZURE_API_KEY']
	openai_api_base = st.secrets['AZURE_API_BASE']
	openai_api_version = st.secrets['AZURE_OPENAI_API_VERSION']

	# Initialize LangChain LLM
	llm = OpenAI(
    	model_name="gpt-4",
    	temperature=0,
    	api_key=openai_api_key,
    	api_base=openai_api_base,
    	api_version=openai_api_version
	)

	# Define tools (e.g., Python REPL)
	tools = [
    	Tool(
        	name="Python REPL",
        	func=PythonREPLTool().run,
        	description="A tool for running Python code and interpreting the results."
    	)
	]

	# Initialize the agent
	agent = initialize_agent(
    	tools=tools,
    	llm=llm,
    	agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    	verbose=True
	)

	return agent
