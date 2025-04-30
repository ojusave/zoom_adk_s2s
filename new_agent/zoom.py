from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import base64
from typing import Dict, Any

# Load environment variables
load_dotenv()

def get_zoom_access_token() -> str:
    """Gets an OAuth access token for the Zoom API."""
    client_id = os.getenv('ZOOM_CLIENT_ID')
    client_secret = os.getenv('ZOOM_CLIENT_SECRET')
    account_id = os.getenv('ZOOM_ACCOUNT_ID')
    
    if not all([client_id, client_secret, account_id]):
        raise ValueError("Missing required Zoom credentials in .env file")
    
    auth_string = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_string}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'account_credentials',
        'account_id': account_id
    }
    
    response = requests.post(
        'https://zoom.us/oauth/token',
        headers=headers,
        data=data
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.text}")
    
    return response.json()['access_token']

def format_zoom_time(dt: datetime) -> str:
    """Format datetime object to Zoom API compatible string."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def create_zoom_meeting(topic: str = "Scheduled Meeting", duration: int = 60, start_time: str = "") -> Dict[str, Any]:
    """Creates a Zoom meeting and returns the join URL."""
    try:
        access_token = get_zoom_access_token()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # If start_time is empty, use current time + 5 minutes
        if not start_time:
            meeting_time = datetime.now() + timedelta(minutes=5)
        else:
            try:
                meeting_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                meeting_time = datetime.now() + timedelta(minutes=5)
        
        # Format time for Zoom API
        zoom_time = format_zoom_time(meeting_time)
        
        meeting_data = {
            'topic': topic,
            'type': 2,  # Scheduled meeting
            'start_time': zoom_time,
            'duration': duration,
            'timezone': 'UTC',
            'settings': {
                'host_video': True,
                'participant_video': True,
                'join_before_host': True,
                'mute_upon_entry': True,
                'auto_recording': 'none'
            }
        }
        
        response = requests.post(
            'https://api.zoom.us/v2/users/me/meetings',
            headers=headers,
            json=meeting_data
        )
        
        if response.status_code != 201:
            return {
                "status": "error",
                "error_message": f"Failed to create meeting: {response.text}"
            }
        
        meeting_info = response.json()
        
        # Format the start time for display
        display_time = meeting_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "status": "success",
            "report": (
                f"✅ Meeting created successfully!\n\n"
                f"📋 Topic: {meeting_info['topic']}\n"
                f"🔗 Join URL: {meeting_info['join_url']}\n"
                f"🆔 Meeting ID: {meeting_info['id']}\n"
                f"⏱️ Duration: {meeting_info['duration']} minutes\n"
                f"🕒 Start Time: {display_time}"
            ),
            "meeting_info": {
                **meeting_info,
                "formatted_start_time": display_time
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error creating meeting: {str(e)}"
        }

# Create the zoom agent
zoom_agent = Agent(
    name="zoom_agent",
    model="gemini-2.0-flash",
    description="Creates Zoom meetings based on email content and requests.",
    instruction="""You are a Zoom meeting scheduler.
Your task is to create appropriate Zoom meetings based on meeting requests.
Extract meeting details from the context and create a meeting accordingly.
Return ONLY the meeting creation response without any additional text.
""",
    tools=[create_zoom_meeting],
    output_key="zoom_meeting_result"
) 