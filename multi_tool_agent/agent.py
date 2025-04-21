from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from multi_tool_agent.extractMetaDataAgent import extract_meta_data_agent
from google.adk.tools.agent_tool import AgentTool
from multi_tool_agent.compareDbAgent import compareDb_data_agent
from multi_tool_agent.sendEmailAgent import Send_Email_Agent
import warnings
from dotenv import load_dotenv
import os
# Ignore all warnings
warnings.filterwarnings("ignore")
import logging
logging.basicConfig(level=logging.ERROR)
load_dotenv()
os.environ["GOOGLE_API_KEY"]

session_service = InMemorySessionService()

APP_NAME = "coordinator"
USER_ID = "user_1"
SESSION_ID = "session_001" 

session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)

metadata_tool = AgentTool(agent=extract_meta_data_agent)
comparison_tool = AgentTool(agent=compareDb_data_agent)
sendEmail_tool = AgentTool(agent=Send_Email_Agent)


root_agent = Agent(
    name="coordinator",
    model="gemini-2.0-flash",
    description="The main coordinator agent. Handles user requests and delegates greetings/farewells and PDF metadata extractor and context-bound Q&A and email related task to specialists.",
    instruction="You are the main coordinator Agent coordinating a team. Your primary responsibility is to provide delegate task to most suitable agent or tools as per user request."
                    "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London')."
                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                    "3. 'metadata_tool': Handles paths and then extract metadata from the given pdf in the form of {name,value} and call comparison_tool"
                    "4. 'comparison_tool': Handles comparison between metadata and customDb"
                    "5. 'sendEmail_tool':Handle email related task"
                    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. If it is path/pdf related delegate to metadata_tool after reciveing response from metadata_tool delegate task to comparison_tool for the comparison of metadata and customDb , performing comaprison is a important task and after getting response from comparison_tool call sendEmail_tool no need to ask recipient email address just execute"
                    "For anything else, respond appropriately or state you cannot handle it.",
    tools=[metadata_tool,comparison_tool,sendEmail_tool]
)

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,  
    session_service=session_service 
)