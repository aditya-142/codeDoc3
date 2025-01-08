import openai
import os
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent
from llama_index.tools.code_interpreter.base import CodeInterpreterToolSpec

def return_agent():
	# API config
	openai.api_type = "azure"
	openai.api_base = os.getenv("AZURE_API_BASE")  # Or use st.secrets['AZURE_API_BASE']
	openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")  # Or st.secrets
	openai.api_key = os.getenv("AZURE_API_KEY")  # Or st.secrets

	code_spec = CodeInterpreterToolSpec()
	tools = code_spec.to_tool_list()
	agent = OpenAIAgent.from_tools(
    	tools,
    	llm=OpenAI(temperature=0, model="gpt-4o"),  
    	verbose=True
	)
	return agent
