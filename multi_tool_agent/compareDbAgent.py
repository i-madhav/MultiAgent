from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import ToolContext
from google import genai
from dotenv import load_dotenv
import os
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

customDB = {
  "document_title": "Annotated Exhibits to the 2021 ISDA Interest Rate Derivatives Definitions",
  "version": "Version 1",
  "date_published": "June 11, 2021",
  "effective_date": "June 11, 2021",
  "copyright_year": "2021",
  "publisher": "International Swaps and Derivatives Association, Inc. (ISDA)",
  "intended_use": "Provides annotated exhibits to the 2021 ISDA Interest Rate Derivatives Definitions, highlighting changes and providing commentary.",
  "key_changes_highlighted": [
    "New fields introduced by the 2021 Definitions (BLUE)",
    "Changes to existing elements in the 2006 Definitions made by the 2021 Definitions (RED)",
    "Notable additions/changes to template (not due to the 2021 Definitions) (ORANGE)",
    "Changes due to Supplement 75/76 (Overnight Rate Compounding/Averaging) (GREEN)"
  ],
  "licensing_note": "Document is created under license from ISDA and should not be used, copied or disseminated other than in accordance with the terms of that license.",
  "disclaimer": "Document is for information purposes only. No representation or warranty is made as to its accuracy, completeness, or suitability for any purpose. ISDA and its affiliates are not liable for any losses incurred as a result of relying upon it. Readers should consult the source documents and external advisors for a definitive view."
}


def comparedata(tool_context:ToolContext):
    """Gets data from customDB and compares it with metaData.
    Returns:
        str: Confidence score as a percentage string (e.g., "80%")
    """
    client = genai.Client(api_key=API_KEY)
    print("Tool: comapredata: called")
    metadata = tool_context.state.get("metaData")
    
    response = client.models.generate_content(
      model="gemini-2.0-flash",
      contents=f"compare {customDB} and {metadata} and give a confidence score , it be in format like only : nn%"
    )
    tool_context.state["confidence_score"] =  response.text
    return f" confidence score is {response.text}%"

compareDb_data_agent = None
try:
  compareDb_data_agent = Agent(
    name="compare_db_with_agent_data_v1",
    model="gemini-2.0-flash",
    description="compare customDb to metadata specialist",
    instruction="You are a compare_db_with_agent_data Agent. Your only task is to comapare the customDb data to metadata , use comapreData tool in order to compare data and return result in the form like n0% : This is your confidence score 'n0%' strictly give response in the form of n0%: and Now send confidence data to send_email_agent , sending data to send_email_agent is a important step to perform , tell coordinator to call sendEmail tool",
    tools=[comparedata]
) 
  print(f"✅ Agent 'compareDb_data' created using model 'gemini-2.0-flash'.")
except Exception as e:
    print(f"❌ Could not create 'compareDb_data'. Check API Key (gemini-2.0-flash). Error: {e}")
    
session_service = InMemorySessionService()
runner = Runner(
    agent= compareDb_data_agent,
    app_name="compareDb_data_agent", 
    session_service=session_service
)