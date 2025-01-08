import streamlit as st
import os
import ast
import logging
import tempfile
from git import Repo
from typing import List, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
from agent import return_agent

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
	file_path: str
	content: str
	module_docstring: Optional[str]
	functions: List[tuple]
	classes: List[tuple]

def is_github_url(url: str) -> bool:
	"""Check if a URL points to a GitHub repository."""
	try:
    	parsed = urlparse(url)
    	return parsed.netloc == "github.com" and len(parsed.path.strip("/").split("/")) >= 2
	except:
    	return False

def clone_github_repo(url: str) -> Tuple[str, tempfile.TemporaryDirectory]:
	"""Clone a GitHub repository to a temporary directory."""
	try:
    	temp_dir = tempfile.TemporaryDirectory()
    	Repo.clone_from(url, temp_dir.name)
    	return temp_dir.name, temp_dir
	except Exception as e:
    	logger.error(f"Error cloning repository: {str(e)}")
    	st.error(f"Failed to clone repository: {str(e)}")
    	raise

@st.cache_data
def get_python_files(directory: str, max_depth: int = 5) -> List[str]:
	"""Retrieve all Python files in a directory up to a maximum depth."""
	python_files = []
	for root, _, files in os.walk(directory):
    	if root[len(directory):].count(os.sep) < max_depth:
        	for file in files:
            	if file.endswith(".py"):
                	python_files.append(os.path.join(root, file))
	return python_files

@st.cache_data
def extract_info(file_path: str) -> Optional[FileInfo]:
	"""Extract relevant information from a Python file."""
	try:
    	with open(file_path, "r", encoding="utf-8") as file:
        	content = file.read()
        	tree = ast.parse(content)

    	module_docstring = ast.get_docstring(tree)
    	functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    	classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    	return FileInfo(
        	file_path=file_path,
        	content=content,
        	module_docstring=module_docstring,
        	functions=[(f.name, ast.get_docstring(f)) for f in functions],
        	classes=[(c.name, ast.get_docstring(c)) for c in classes],
    	)
	except Exception as e:
    	logger.error(f"Error parsing {file_path}: {str(e)}")
    	return None

def main():
	st.title("Code Product Documentation Generator (LangChain)")
	st.markdown("Generate comprehensive documentation for Python projects using LangChain.")

	input_path = st.text_input(
    	"Enter the directory path or GitHub repository URL:",
    	help="Enter a local directory path or GitHub repo URL (e.g., https://github.com/user/repo)."
	)
	template = st.text_area(
    	"Enter the documentation template:",
    	value="# Project Overview\n## Installation\n## Usage\n## API Reference\n## Contributing",
    	help="Specify the structure of the generated documentation in Markdown format."
	)

	if input_path and st.button("Generate Documentation"):
    	with st.spinner("Processing input..."):
        	temp_dir = None
        	directory_path = input_path

        	if is_github_url(input_path):
            	try:
                	directory_path, temp_dir = clone_github_repo(input_path)
            	except Exception:
                	return

        	if not os.path.exists(directory_path):
            	st.error("Invalid directory path.")
            	return

        	python_files = get_python_files(directory_path)
        	project_info = [extract_info(file) for file in python_files if extract_info(file)]

        	file_summaries = "\n".join(
            	f"File: {info.file_path}\nModule Docstring: {info.module_docstring}\n"
            	f"Functions: {info.functions}\nClasses: {info.classes}\n"
            	for info in project_info if info
        	)

        	# Generate documentation using the LangChain agent
        	agent = return_agent()
        	prompt = f"""
        	Generate comprehensive documentation for the following Python project:

        	Project Structure:
        	{', '.join(info.file_path for info in project_info)}

        	File Summaries:
        	{file_summaries}

        	Documentation Template:
        	{template}

        	Provide detailed documentation that explains the project's purpose, components, and interactions.
        	"""
        	try:
            	result = agent.run(prompt)
            	st.markdown("## Generated Documentation")
            	st.markdown(result)
        	except Exception as e:
            	logger.error(f"Error generating documentation: {str(e)}")
            	st.error("Failed to generate documentation. Please check your input and try again.")
        	finally:
            	if temp_dir:
                	temp_dir.cleanup()

if __name__ == "__main__":
	main()

