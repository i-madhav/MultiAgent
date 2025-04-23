from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import ToolContext
from PyPDF2 import PdfReader
from google import genai
from dotenv import load_dotenv
import os
import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")
import logging
logging.basicConfig(level=logging.ERROR)

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

def parse_given_path(pdf_path: str,tool_context:ToolContext):
       """
    Retrieves the content of the pdf on the given path
         Args:
      pdf_path (str): like ex: "C:/Users/madha/Downloads/MadhavSharmaResume.pdf"
     return the metaData in the form of {name,value}
    """
       client = genai.Client(api_key=API_KEY)
       try:
           print("Tool: parse_given_path: called")
           reader = PdfReader(pdf_path)
           text = ""
           for page in reader.pages:
               text += page.extract_text()
           response = client.models.generate_content(
                        model="gemini-2.0-flash", contents=f"extract the metadatas from the given text {text},give response in the form of {{name,value}} json object"
                            )
           tool_context.state["metaData"] = response.text
       except Exception as e:
           return f"Error reading PDF: {e}"
    

extract_meta_data_agent = Agent(
    name="extract_meta_data_agent",
    model="gemini-2.0-flash",
    description="PDF metadata extraction specialist",
    instruction="""**PDF Metadata Workflow**
1. Request PDF path
2. Extract & store metadata
3. Present in {name:value} format
4. send to compareDb agent
""",
    tools=[parse_given_path]
)

session_service = InMemorySessionService()

runner = Runner(
    agent=extract_meta_data_agent,
    app_name="extract_meta_data_agent", 
    session_service=session_service
)