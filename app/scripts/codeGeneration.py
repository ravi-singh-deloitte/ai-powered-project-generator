import os
import subprocess
from dotenv import load_dotenv
from typing_extensions import TypedDict, List
from io import BytesIO
from docx import Document

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import Docx2txtLoader
from langgraph.graph import StateGraph, START, END
import zipfile

load_dotenv()
class Data(TypedDict):
    api_endpoints: List[str]
    auth_requirements: List[str]
    backend_logic: List[str]
    database_schema: List[str]

class State(TypedDict):
    document: str
    parsed_data: str
    folder_structure: str

class CodeGenerator:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=1.0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.folder_structure = self._load_folder_structure()
        self.graph_executor = self._generate_graph()
    
    def zip_folder(self, folder_path, output_path):
        with zipfile.ZipFile(output_path, 'w') as zip_file:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, folder_path)
                    zip_file.write(file_path, rel_path)

    def _load_folder_structure(self):
        print("Loading folder structure...")
        loader = Docx2txtLoader("./assets/folderStructure.docx")
        return loader.load()

    def extract_text(self, state: State) -> State:
        print("\nExtracting text from uploaded DOCX file...")
        doc = Document(BytesIO(state["document"]))
        full_text = "\n".join([p.text for p in doc.paragraphs])
        return {
            "document": full_text,
            "parsed_data": "",
            "folder_structure": self.folder_structure,
        }

    def analyse_document(self, state: State) -> State:
        print("\nAnalyzing the document to extract requirements...")
        prompt = ChatPromptTemplate.from_template(
            "Parse the document to get the information about api_endpoints, backend_logic, database_schema and auth_requirements: {document}"
        )
        chain = prompt | self.llm
        parsed_output = chain.invoke({"document": state["document"]}).content
        return {
            **state,
            "parsed_data": parsed_output,
        }

    def generate_code(self, state: State) -> State:
        print("\nGenerating code based on parsed data and folder structure...")
        prompt = ChatPromptTemplate.from_template(
             """Generate detail code that creates all necessary files and folders and with error handling according to the specified 
                folder structure: {folder_structure}. Populate these files with the required all necessary code 
                based on the parsed data: {parsed_data}. Include all necessary modules, classes,
                and functions according to the requirements specified in the document.
                Output only the code,without python marker, without any markdown formatting,without any code block markers(e.g. python, ```), or any additional text and only import 'os'.
                Generate a single root folder generated_project.
                """       
        )
        chain = prompt | self.llm
        output_code = chain.invoke({
            "parsed_data": state["parsed_data"],
            "folder_structure": state["folder_structure"]
        }).content

        script_path = "generated_script.py"
        with open(script_path, 'w') as f:
            f.write(output_code)

        try:
            subprocess.run(["python", script_path], check=True)
            self.zip_folder("generated_project", "generated_project.zip")
        except subprocess.CalledProcessError as error:
            print(f"Error running script: {error}")

        return state

    def _generate_graph(self):
        workflow = StateGraph(State)

        workflow.add_node("extract_text", self.extract_text)
        workflow.add_node("analyse_document", self.analyse_document)
        workflow.add_node("generate_code", self.generate_code)

        workflow.add_edge(START,"extract_text")
        workflow.add_edge("extract_text", "analyse_document")
        workflow.add_edge("analyse_document", "generate_code")
        workflow.add_edge("generate_code", END)

        return workflow.compile()

    def run(self, file_bytes: bytes):
        initial_state = {
            "document": file_bytes,
            "parsed_data": "",
            "folder_structure": "", 
        }
        return self.graph_executor.invoke(initial_state)

code_generator = CodeGenerator()
