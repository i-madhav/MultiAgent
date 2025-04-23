from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import ToolContext
from dotenv import load_dotenv
import os
load_dotenv()
os.environ["RESEND_API_KEY"]
import resend


def sendEmail(tool_context:ToolContext):
    """
    You send send email no need to ask for email from the user just execute the function
    """
    print("Tool: sendEmail: called")
    r = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "spacefatcsyou@gmail.com",
        "subject": "Hello World",
        "html": f"<p>Your Trade is confirmed</p> <p>This is confidence score {tool_context.state.get("confidence_score")}</p>"
        })
    return r 

Send_Email_Agent = None
try:
    Send_Email_Agent = Agent(
        name="Send_Email_Agent_v1",
        model="gemini-2.0-flash",
        description="You are a agent specialised in sending the email",
        instruction="You are a agent specialised in sending email , for sending you use sendEmail tool only . No need to ask user for email just execute the sendEmail Tool",
        tools=[sendEmail]
    )
    print(f"✅ Agent 'Send_Email_Agent' created using model 'gemini-2.0-flash'.")
except Exception as e:
    print(f"❌ Could not create 'Send_Email_Agent'. Check API Key (gemini-2.0-flash). Error: {e}")
    
session_service = InMemorySessionService()
runner = Runner(
    agent= Send_Email_Agent,
    app_name="Send_Email_Agent_v1", 
    session_service=session_service
)