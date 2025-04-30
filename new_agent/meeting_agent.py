from typing import Dict, Any
from datetime import datetime, timedelta
import subprocess
import platform
import webbrowser
from google.adk.agents import Agent

def open_zoom_url(url: str) -> Dict[str, Any]:
    """Opens a Zoom URL using the system's default browser or Zoom app.
    
    Args:
        url: The Zoom meeting URL to open
        
    Returns:
        dict: Status and result of the operation
    """
    try:
        # Open URL with system's default handler (should trigger Zoom app)
        webbrowser.open(url)
        
        return {
            "status": "success",
            "report": f"🚀 Joining Zoom meeting: {url}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to open Zoom meeting: {str(e)}"
        }

def check_upcoming_meetings() -> Dict[str, Any]:
    """Check for meetings starting in the next 5 minutes.
    
    Returns:
        dict: Status and any meetings that need to be joined
    """
    try:
        from .calendar import calendar_storage
        
        now = datetime.now()
        five_mins_future = now + timedelta(minutes=5)
        
        upcoming_meetings = []
        for event in calendar_storage.events:
            try:
                start_time = datetime.strptime(event['start_time'], "%Y-%m-%d %H:%M:%S")
                # Check if meeting starts within next 5 minutes and hasn't been joined
                if now <= start_time <= five_mins_future and not event.get('joined', False):
                    upcoming_meetings.append(event)
                    # Mark meeting as joined to prevent duplicate joins
                    event['joined'] = True
            except (ValueError, KeyError):
                continue
        
        if not upcoming_meetings:
            return {
                "status": "success",
                "report": "No upcoming meetings to join.",
                "meetings": []
            }
        
        meetings_report = "\n\n".join([
            f"📅 Meeting: {meeting['title']}\n"
            f"🕒 Start: {meeting['start_time']}\n"
            f"🔗 URL: {meeting['meeting_url']}"
            for meeting in upcoming_meetings
        ])
        
        return {
            "status": "success",
            "report": f"Found {len(upcoming_meetings)} meeting(s) to join:\n\n{meetings_report}",
            "meetings": upcoming_meetings
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to check upcoming meetings: {str(e)}"
        }

# Create the meeting agent
meeting_agent = Agent(
    name="meeting_agent",
    model="gemini-2.0-flash",
    description="Monitors calendar and joins upcoming Zoom meetings",
    instruction="""You are a meeting attendance assistant.
Your tasks:
1. Check for meetings starting in the next 5 minutes
2. If found, join them using the Zoom URL
3. Confirm when you've joined a meeting

Rules:
- Only join meetings that start within 5 minutes
- Don't join meetings that have already been joined
- Provide clear confirmation when joining meetings
""",
    tools=[check_upcoming_meetings, open_zoom_url],
    output_key="meeting_join_result"
) 