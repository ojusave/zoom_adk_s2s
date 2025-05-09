from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import os
import requests
import webbrowser
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
        time_str = time_str.lower().strip()
        
        # Handle "in X days" format
        if "in" in time_str and "days" in time_str:
            try:
                days = int(time_str.split("in")[1].split("days")[0].strip())
                date = datetime.now() + timedelta(days=days)
                time_part = time_str.split("at")[-1].strip() if "at" in time_str else "00:00:00"
                
                if "pm" in time_part:
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
                
                return datetime.strptime(f"{date.strftime('%Y-%m-%d')} {time}", "%Y-%m-%d %H:%M:%S")
            except (ValueError, IndexError):
                pass

        # Handle month names (e.g., "may 12th")
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        for month_name, month_num in months.items():
            if month_name in time_str:
                try:
                    # Extract the day
                    day_part = time_str.split(month_name)[1].strip()
                    day = int(''.join(filter(str.isdigit, day_part)))
                    
                    # Get current year
                    year = datetime.now().year
                    
                    # Extract time if present
                    time_part = time_str.split("at")[-1].strip() if "at" in time_str else "00:00:00"
                    
                    if "pm" in time_part:
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
                    
                    return datetime.strptime(f"{year}-{month_num:02d}-{day:02d} {time}", "%Y-%m-%d %H:%M:%S")
                except (ValueError, IndexError):
                    pass
        
        # Handle "tomorrow" format
        if "tomorrow" in time_str:
            date = datetime.now() + timedelta(days=1)
            time_part = time_str.replace('tomorrow', '').strip()
            
            if "pm" in time_part:
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
            
            return datetime.strptime(f"{date.strftime('%Y-%m-%d')} {time}", "%Y-%m-%d %H:%M:%S")
        
        # Handle today with time
        elif any(x in time_str for x in ["am", "pm"]):
            now = datetime.now()
            time_part = time_str.lower()
            
            if "pm" in time_part:
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

def get_zoom_meeting(meeting_id: str) -> Dict[str, Any]:
    """Gets details of a specific Zoom meeting."""
    try:
        access_token = get_zoom_access_token()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'https://api.zoom.us/v2/meetings/{meeting_id}',
            headers=headers
        )
        
        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Failed to get meeting: {response.text}"
            }
        
        meeting_info = response.json()
        
        # Parse the start time from Zoom's format
        start_time = datetime.strptime(meeting_info['start_time'], "%Y-%m-%dT%H:%M:%SZ")
        display_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "status": "success",
            "message": "Meeting details retrieved successfully!",
            "details": {
                "topic": meeting_info['topic'],
                "join_url": f"[Click to join]({meeting_info['join_url']})",
                "start_url": meeting_info.get('start_url', ''),
                "meeting_id": meeting_info['id'],
                "duration": f"{meeting_info['duration']} minutes",
                "start_time": display_time,
                "status": meeting_info['status']
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting meeting: {str(e)}"
        }

def list_zoom_meetings(from_date: Optional[str] = None, to_date: Optional[str] = None) -> Dict[str, Any]:
    """Lists Zoom meetings within a specified timeframe.
    
    Args:
        from_date: Start date in format 'YYYY-MM-DD' (optional, defaults to today)
        to_date: End date in format 'YYYY-MM-DD' (optional, defaults to 7 days from from_date)
    """
    try:
        access_token = get_zoom_access_token()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Handle date parameters
        if not from_date:
            from_date = datetime.now().strftime("%Y-%m-%d")
        if not to_date:
            # Default to 7 days from from_date if not specified
            to_date = (datetime.strptime(from_date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
            
        # Convert dates to datetime objects for comparison
        from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
        to_datetime = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)  # Include the entire end date
        
        params = {
            'type': 'scheduled',
            'page_size': 100  # Maximum allowed by Zoom
        }
        
        response = requests.get(
            'https://api.zoom.us/v2/users/me/meetings',
            headers=headers,
            params=params
        )
        
        if response.status_code == 401:
            return {
                "status": "error",
                "message": "Authentication failed. Please check your Zoom credentials."
            }
        elif response.status_code != 200:
            error_message = response.json().get('message', response.text) if response.text else 'Unknown error'
            return {
                "status": "error",
                "message": f"Failed to list meetings: {error_message}"
            }
        
        meetings_data = response.json()
        filtered_meetings = []
        
        # Check if meetings exist in the response
        if 'meetings' not in meetings_data:
            return {
                "status": "success",
                "message": "No scheduled meetings found",
                "meetings": []
            }
        
        for meeting in meetings_data['meetings']:
            try:
                # Handle cases where start_time might not be present
                if 'start_time' not in meeting:
                    continue
                    
                meeting_time = datetime.strptime(meeting['start_time'], "%Y-%m-%dT%H:%M:%SZ")
                
                if from_datetime <= meeting_time <= to_datetime:
                    filtered_meetings.append({
                        "topic": meeting.get('topic', 'Untitled Meeting'),
                        "meeting_id": meeting.get('id', 'N/A'),
                        "start_time": meeting_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "duration": f"{meeting.get('duration', 0)} minutes",
                        "join_url": f"[Click to join]({meeting.get('join_url', '#')})",
                        "status": meeting.get('status', 'unknown')
                    })
            except (ValueError, KeyError) as e:
                # Skip meetings with invalid data
                continue
        
        # Create table format
        table_rows = []
        for meeting in filtered_meetings:
            table_rows.append({
                "Topic": meeting["topic"],
                "Date": meeting["start_time"].split()[0],
                "Time": meeting["start_time"].split()[1],
                "Duration": meeting["duration"],
                "Meeting ID": meeting["meeting_id"],
                "Join Link": meeting["join_url"]
            })
        
        return {
            "status": "success",
            "message": f"Found {len(filtered_meetings)} meetings between {from_date} and {to_date}",
            "meetings": filtered_meetings,
            "table_format": {
                "headers": ["Topic", "Date", "Time", "Duration", "Meeting ID", "Join Link"],
                "rows": table_rows
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing meetings: {str(e)}"
        }

def open_zoom_url(url: str) -> None:
    """Opens a Zoom URL in the default web browser."""
    try:
        # Clean the URL if it's in markdown format
        if url.startswith('[') and '](' in url:
            url = url.split('](')[1].rstrip(')')
        # Ensure the URL is properly formatted
        if not url.startswith('http'):
            url = 'https://' + url
        # Open in new tab
        webbrowser.open(url, new=2)
    except Exception as e:
        print(f"Error opening URL: {str(e)}")

def start_zoom_meeting(meeting_id: str) -> Dict[str, Any]:
    """Starts a Zoom meeting by opening the start URL in a new tab."""
    try:
        # First try to get the meeting by ID
        meeting_info = get_zoom_meeting(meeting_id)
        
        # If that fails, try to find the meeting by topic
        if meeting_info["status"] == "error":
            # List all meetings
            meetings = list_zoom_meetings()
            if meetings["status"] == "success":
                # Find the meeting with matching topic
                for meeting in meetings.get("meetings", []):
                    if meeting["topic"].lower() == meeting_id.lower():
                        meeting_info = get_zoom_meeting(meeting["meeting_id"])
                        break
        
        if meeting_info["status"] == "success":
            # Extract the start URL from the meeting details
            start_url = meeting_info["details"].get("start_url")
            if start_url:
                open_zoom_url(start_url)
                return {
                    "status": "success",
                    "message": f"Opening meeting '{meeting_info['details']['topic']}' in a new tab..."
                }
            else:
                # If no start URL is available, provide the join URL instead
                join_url = meeting_info["details"].get("join_url", "")
                if join_url:
                    open_zoom_url(join_url)
                    return {
                        "status": "success",
                        "message": f"Opening meeting '{meeting_info['details']['topic']}' in a new tab...\nNote: You may need to sign in to Zoom to start the meeting as host."
                    }
                else:
                    return {
                        "status": "error",
                        "message": "No start or join URL found for this meeting. Please check your Zoom account permissions."
                    }
        return meeting_info
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error starting meeting: {str(e)}"
        }

def join_zoom_meeting(meeting_id: str) -> Dict[str, Any]:
    """Joins a Zoom meeting by opening the join URL in a new tab."""
    try:
        # First try to get the meeting by ID
        meeting_info = get_zoom_meeting(meeting_id)
        
        # If that fails, try to find the meeting by topic
        if meeting_info["status"] == "error":
            # List all meetings
            meetings = list_zoom_meetings()
            if meetings["status"] == "success":
                # Find the meeting with matching topic
                for meeting in meetings.get("meetings", []):
                    if meeting["topic"].lower() == meeting_id.lower():
                        meeting_info = get_zoom_meeting(meeting["meeting_id"])
                        break
        
        if meeting_info["status"] == "success":
            # Extract the join URL from the meeting details
            join_url = meeting_info["details"].get("join_url")
            if join_url:
                open_zoom_url(join_url)
                return {
                    "status": "success",
                    "message": f"Opening meeting '{meeting_info['details']['topic']}' in a new tab..."
                }
            else:
                return {
                    "status": "error",
                    "message": "Join URL not found for this meeting"
                }
        return meeting_info
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error joining meeting: {str(e)}"
        } 