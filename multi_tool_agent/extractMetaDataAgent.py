from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import ToolContext
from PyPDF2 import PdfReader
import os
import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")
import logging
logging.basicConfig(level=logging.ERROR)

def parse_given_path(pdf_path: str, tool_context:ToolContext) -> dict:
    """Retrieves the content of the pdf on the given path
         Args:
      pdf_path (str): like ex: "C:/Users/madha/Downloads/MadhavSharmaResume.pdf"
      return {name,value}
    """
    try:
        print("Tool: parse_given_path:called")
        pdf_reader = PdfReader(pdf_path)
        metadata = []
        
        # Extract standard metadata
        if pdf_reader.metadata:
            for key, value in pdf_reader.metadata.items():
                clean_key = key.replace("/", "").strip()
                metadata.append({
                    "name": clean_key,
                    "value": str(value)
                })
        
        # Add custom fields
        metadata.extend([
            {"name": "TotalPages", "value": str(len(pdf_reader.pages))},
            {"name": "FileName", "value": os.path.basename(pdf_path)}
        ])
        tool_context.state["metaData"] = metadata
        return metadata
    except Exception as e:
        return {"status": "error", "message": f"PDF processing failed: {str(e)}"}


# def get_vector_store(text_chunks):
#     embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
#     vector_store = FAISS.from_texts(text_chunks, embeddings)
#     vector_store.save_local("faiss_index_meta_data")
#     return True
    
# def get_text_chunks(text):
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
#     chunks = text_splitter.split_text(text)
#     return chunks
    

extract_meta_data_agent = Agent(
    name="extract_meta_data_agent",
    model="gemini-2.0-flash",
    description="PDF metadata extraction specialist",
    instruction="""**PDF Metadata Workflow**
1. Request PDF path
2. Extract & store metadata
3. Present in {name:value} format
""",
    tools=[parse_given_path]
)

session_service = InMemorySessionService()

runner = Runner(
    agent=extract_meta_data_agent,
    app_name="extract_meta_data_agent", 
    session_service=session_service
)