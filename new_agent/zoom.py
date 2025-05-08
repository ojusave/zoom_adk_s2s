from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from .zoom_oauth import get_zoom_access_token

# Load environment variables
load_dotenv()

def format_zoom_time(dt: datetime) -> str:
    """Format datetime object to Zoom API compatible string."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_meeting_time(time_str: str = "") -> datetime:
    """Parse meeting time from various formats including natural language."""
    try:
        if not time_str:
            return datetime.now() + timedelta(minutes=5)
        
        # Try to parse the time string
        if "tomorrow" in time_str.lower():
            date = datetime.now() + timedelta(days=1)
            time = "00:00:00"  # default
            time_part = time_str.lower().replace('tomorrow', '').strip()
            
            if "pm" in time_part:
                # Handle time with minutes (3.30 pm or 3:30 pm)
                time_digits = time_part.split('pm')[0].strip().replace('.', ':')
                if ':' in time_digits:
                    hour, minutes = map(int, time_digits.split(':'))
                    if hour != 12:
                        hour += 12
                    time = f"{hour:02d}:{minutes:02d}:00"
                else:
                    hour = int(time_digits)
                    if hour != 12:
                        hour += 12
                    time = f"{hour:02d}:00:00"
            elif "am" in time_part:
                # Handle time with minutes (3.30 am or 3:30 am)
                time_digits = time_part.split('am')[0].strip().replace('.', ':')
                if ':' in time_digits:
                    hour, minutes = map(int, time_digits.split(':'))
                    if hour == 12:
                        hour = 0
                    time = f"{hour:02d}:{minutes:02d}:00"
                else:
                    hour = int(time_digits)
                    if hour == 12:
                        hour = 0
                    time = f"{hour:02d}:00:00"
            
            return datetime.strptime(f"{date.strftime('%Y-%m-%d')} {time}", "%Y-%m-%d %H:%M:%S")
        
        elif any(x in time_str.lower() for x in ["am", "pm"]):
            # Today at given time
            now = datetime.now()
            time_part = time_str.lower()
            
            if "pm" in time_part:
                # Handle time with minutes (3.30 pm or 3:30 pm)
                time_digits = time_part.split('pm')[0].strip().replace('.', ':')
                if ':' in time_digits:
                    hour, minutes = map(int, time_digits.split(':'))
                    if hour != 12:
                        hour += 12
                    time = f"{hour:02d}:{minutes:02d}:00"
                else:
                    hour = int(time_digits)
                    if hour != 12:
                        hour += 12
                    time = f"{hour:02d}:00:00"
            elif "am" in time_part:
                # Handle time with minutes (3.30 am or 3:30 am)
                time_digits = time_part.split('am')[0].strip().replace('.', ':')
                if ':' in time_digits:
                    hour, minutes = map(int, time_digits.split(':'))
                    if hour == 12:
                        hour = 0
                    time = f"{hour:02d}:{minutes:02d}:00"
                else:
                    hour = int(time_digits)
                    if hour == 12:
                        hour = 0
                    time = f"{hour:02d}:00:00"
            else:
                time = "00:00:00"
            
            return datetime.strptime(f"{now.strftime('%Y-%m-%d')} {time}", "%Y-%m-%d %H:%M:%S")
        else:
            # Try to parse as exact datetime
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # If parsing fails, return current time + 5 minutes
        return datetime.now() + timedelta(minutes=5)

def create_zoom_meeting(topic: str = "Scheduled Meeting", duration: int = 60, start_time: str = "") -> Dict[str, Any]:
    """Creates a Zoom meeting and returns the join URL."""
    try:
        access_token = get_zoom_access_token()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Parse the start time using shared function
        meeting_time = parse_meeting_time(start_time)
        
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
                "message": f"Failed to create meeting: {response.text}"
            }
        
        meeting_info = response.json()
        
        # Format the start time for display
        display_time = meeting_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "status": "success",
            "message": "Meeting created successfully!",
            "details": {
                "topic": meeting_info['topic'],
                "join_url": f"[Click to join]({meeting_info['join_url']})",
                "meeting_id": meeting_info['id'],
                "duration": f"{meeting_info['duration']} minutes",
                "start_time": display_time
            },
            "actions": {
                "start_meeting": f"[Click to start]({meeting_info['start_url']})",
                "edit_meeting": {
                    "meeting_id": meeting_info['id'],
                    "current_details": {
                        "topic": meeting_info['topic'],
                        "duration": meeting_info['duration'],
                        "start_time": display_time
                    }
                },
                "delete_meeting": {
                    "meeting_id": meeting_info['id']
                }
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating meeting: {str(e)}"
        }

def update_zoom_meeting(meeting_id: Optional[str], topic: Optional[str] = None, duration: Optional[int] = None, start_time: Optional[str] = None) -> Dict[str, Any]:
    """Updates a Zoom meeting's details and returns updated details."""
    try:
        access_token = get_zoom_access_token()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Prepare update data
        update_data = {}
        if topic:
            update_data['topic'] = topic
        if duration:
            update_data['duration'] = duration
        if start_time:
            try:
                # Use shared time parsing function
                meeting_time = parse_meeting_time(start_time)
                update_data['start_time'] = format_zoom_time(meeting_time)
            except Exception:
                return {
                    "status": "error",
                    "message": "Invalid start time format. Please use YYYY-MM-DD HH:MM:SS or a natural language time like 'tomorrow 1 pm' or '1 pm'"
                }
        
        response = requests.patch(
            f'https://api.zoom.us/v2/meetings/{meeting_id}',
            headers=headers,
            json=update_data
        )
        
        if response.status_code != 204:
            return {
                "status": "error",
                "message": f"Failed to update meeting: {response.text}"
            }
        
        # Fetch updated meeting details
        get_response = requests.get(
            f'https://api.zoom.us/v2/meetings/{meeting_id}',
            headers=headers
        )
        if get_response.status_code != 200:
            return {
                "status": "error",
                "message": f"Meeting updated but failed to fetch updated details: {get_response.text}"
            }
        meeting_info = get_response.json()
        display_time = meeting_info['start_time'].replace('T', ' ').replace('Z', '')
        return {
            "status": "success",
            "message": "Meeting updated successfully!",
            "details": {
                "topic": meeting_info.get('topic', ''),
                "join_url": f"[Click to join]({meeting_info.get('join_url', '')})",
                "meeting_id": meeting_info.get('id', meeting_id),
                "duration": f"{meeting_info.get('duration', '')} minutes",
                "start_time": display_time
            },
            "actions": {
                "start_meeting": f"[Click to start]({meeting_info.get('start_url', '')})",
                "edit_meeting": {
                    "meeting_id": meeting_info.get('id', meeting_id),
                    "current_details": {
                        "topic": meeting_info.get('topic', ''),
                        "duration": meeting_info.get('duration', ''),
                        "start_time": display_time
                    }
                },
                "delete_meeting": {
                    "meeting_id": meeting_info.get('id', meeting_id)
                }
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error updating meeting: {str(e)}"
        }

def delete_zoom_meeting(meeting_id: str) -> Dict[str, Any]:
    """Deletes a Zoom meeting."""
    try:
        access_token = get_zoom_access_token()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.delete(
            f'https://api.zoom.us/v2/meetings/{meeting_id}',
            headers=headers
        )
        
        if response.status_code != 204:
            return {
                "status": "error",
                "message": f"Failed to delete meeting: {response.text}"
            }
        
        return {
            "status": "success",
            "message": "Meeting deleted successfully!"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error deleting meeting: {str(e)}"
        }

# Create the zoom agent
zoom_agent = Agent(
    name="zoom_agent",
    model="gemini-2.0-flash",
    description="Creates Zoom meetings based on email content and requests.",
    instruction="""You are a Zoom meeting scheduler.
Your task is to create appropriate Zoom meetings based on meeting requests. If user does not provide you with relevant details, use placeholder values.
Extract meeting details from the context and create a meeting accordingly.
Return ONLY the meeting creation response without any additional text.
""",
    tools=[create_zoom_meeting],
    output_key="zoom_meeting_result"
) 