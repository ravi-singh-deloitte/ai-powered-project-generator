import os 
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langchain_community.document_loaders import Docx2txtLoader
from typing_extensions import TypedDict, List
from langchain_core.prompts import ChatPromptTemplate
from docx import Document
from io import BytesIO
load_dotenv()

class State(TypedDict):
    api_endpoints: List[str]
    backend_logic: List[str]
    database_schema: List[str]
    auth_requirements: List[str]

class State(TypedDict):
    document: str
    parsed_data: List[State]

class CodeGenerator:
    def __init__(self):
        self.workflow = StateGraph(State)
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.doc_content = None
        self.llm.invoke("Hey GroqAI, Good Morning!")

    def parse_document(self, state: State):
        print("\nParsing the document to get requirements and data...")
        prompt = ChatPromptTemplate.from_template(
            "Parse the document to get the information about api_endpoints, backend_logic, database_schema and auth_requirements: {document}"
        )
        chain = prompt | self.llm
        output = chain.invoke({"document": state["document"]}).content
        print({"parsed_data": output})
        return {"parsed_data": output}

    def extract_text_from_docx(self, file_content):
        doc = Document(BytesIO(file_content))
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        self.doc_content = '\n'.join(full_text)
        state = {"document": self.doc_content, "parsed_data": []}
        return self.parse_document(state)

code_generator = CodeGenerator()