from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import ToolContext

customDB = [
  { "name": "Title", "value": "ISDA 2021 Definitions Consolidated Confirmation Templates - COLOUR CODED" },
  { "name": "Version", "value": "1.0" },
  { "name": "Publication Date", "value": "June 11, 2021" },
  { "name": "Effective Date", "value": "June 11, 2021" },
  { "name": "Publisher", "value": "International Swaps and Derivatives Association, Inc. (ISDA)" },
  { "name": "Copyright", "value": "© 2021 by International Swaps and Derivatives Association, Inc." },
  { "name": "Document Type", "value": "Annotated Exhibits to the 2021 ISDA Interest Rate Derivatives Definitions" },
  { "name": "Purpose", "value": "Information and commentary on changes from the 2006 ISDA Definitions" },
  { "name": "Color Coding Notes", "value": "BLUE = New in 2021, RED = Changes from 2006, ORANGE = Template updates, GREEN = Supplement 75/76 changes" }
]


def comparedata(tool_context:ToolContext):
    """Gets data from customDB and compares it with metaData.
    Returns:
        str: Confidence score as a percentage string (e.g., "80%")
    """
    
    print("Tool:comapredata: called")
    metadata = tool_context.state.get("metaData")
    matches = 0
    total = len(customDB)
    for item in customDB:
        for res in metadata:
            if item["name"] == res["name"] or item["value"] == res["value"]:
                matches += 1
                break 
    
    confidence = (matches / total) * 100
    tool_context.state["confidence_score"] =  confidence
    print("This is confidence")
    print(confidence)
    return f" confidence score is {confidence:.0f}%"

compareDb_data_agent = None
try:
  compareDb_data_agent = Agent(
    name="compare_db_with_agent_data_v1",
    model="gemini-2.0-flash",
    description="compare customDb to metadata specialist",
    instruction="You are a compare_db_with_agent_data Agent. Your only task is to comapare the customDb data to metadata , use comapreData tool in order to compare data and return result in the form like n0% : This is your confidence score 'n0%' and Now send confidence data to send_email_agent , sending data to send_email_agent is a important step to perform",
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