import os
import subprocess
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_community.document_loaders import Docx2txtLoader
from typing_extensions import TypedDict, List
from langchain_core.prompts import ChatPromptTemplate
from docx import Document
from io import BytesIO

load_dotenv()
class ParsedData(TypedDict):
    api_endpoints: List[str]
    auth_requirements: List[str]
    backend_logic: List[str]
    database_schema: List[str]

class State(TypedDict):
    document: str
    folder_structure: str
    parsed_data: List[ParsedData]

class CodeGenerator:
    def __init__(self):
        self.workflow = StateGraph(State)
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=1.0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.doc_content = None
        loader = Docx2txtLoader("./assets/folderStructure.docx")
        self.folder_structure_content = loader.load()

    def generate_code(self, state: State):
     print("\nGenerating code based after analysing the document")
     prompt = ChatPromptTemplate.from_template(
        """Generate code that creates all necessary files and folders according to the specified 
        folder structure: {folder_structure}. Populate these files with the required code 
        based on the parsed data: {parsed_data}. Include all necessary modules, classes,
        and functions according to the requirements specified in the document.
        Output only the code,without python marker, without any markdown formatting,without any code block markers(e.g. python, ```), or any additional text and only import 'os'.
        Generate a single root folder generated_project."""              
        )
     chain = prompt | self.llm
     output = chain.invoke({"parsed_data": state["parsed_data"], "folder_structure": state["folder_structure"]}).content
     print(output)
     script_path = "generated_script.py"
     with open(script_path, 'w') as f:
        f.write(output)
     try:
        subprocess.run(["python", script_path], check=True)
     except subprocess.CalledProcessError as error:
        print(f"Error running script: {error}")
     return output

    def analyse_document(self, state: State):
        print("\Analysing the document to get requirements...")
        prompt = ChatPromptTemplate.from_template(
            "Parse the document to get the information about api_endpoints, backend_logic, database_schema and auth_requirements: {document}"
        )
        chain = prompt | self.llm
        output = chain.invoke({"document": state["document"]}).content
        state["parsed_data"] = output
        return self.generate_code(state)

    def extract_text(self, file_content):
        doc = Document(BytesIO(file_content))
        full_text = [paragraph.text for paragraph in doc.paragraphs]
        doc_content = '\n'.join(full_text)
        state = {"document": doc_content, "parsed_data": "", "folder_structure": self.folder_structure_content}
        return self.analyse_document(state)

code_generator = CodeGenerator()