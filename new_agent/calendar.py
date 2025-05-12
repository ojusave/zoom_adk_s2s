from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

# Mock calendar storage
class CalendarStorage:
    def __init__(self):
        self.calendar_file = "mock_calendar.json"
        self._load_calendar()

    def _load_calendar(self):
        """Load calendar from file or create new if doesn't exist"""
        if os.path.exists(self.calendar_file):
            with open(self.calendar_file, 'r') as f:
                self.events = json.load(f)
        else:
            self.events = []
            self._save_calendar()

    def _save_calendar(self):
        """Save calendar to file"""
        with open(self.calendar_file, 'w') as f:
            json.dump(self.events, f, indent=2)

    def add_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add new event to calendar"""
        event = {
            "id": str(len(self.events) + 1),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **event_data
        }
        self.events.append(event)
        self._save_calendar()
        return event

    def list_events(self, date: str = None) -> List[Dict[str, Any]]:
        """List events, optionally filtered by date"""
        if date:
            return [
                event for event in self.events 
                if event.get("date", "").startswith(date)
            ]
        return self.events

# Initialize calendar storage
calendar_storage = CalendarStorage()

def add_to_calendar(
    title: str,
    start_time: str = "",
    duration: int = 60,
    meeting_url: str = "",
    meeting_id: str = "",
    description: str = ""
) -> Dict[str, Any]:
    """Add a meeting to the calendar.
    
    Args:
        title: Meeting title/topic
        start_time: Meeting start time (YYYY-MM-DD HH:MM:SS format)
        duration: Meeting duration in minutes
        meeting_url: Zoom meeting URL
        meeting_id: Zoom meeting ID
        description: Meeting description
        
    Returns:
        dict: Status and event details
    """
    try:
        # If no start time provided, use current time
        if not start_time:
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        event_data = {
            "title": title,
            "start_time": start_time,
            "duration": duration,
            "meeting_url": meeting_url,
            "meeting_id": meeting_id,
            "description": description,
            "type": "zoom_meeting"
        }

        event = calendar_storage.add_event(event_data)

        return {
            "status": "success",
            "report": (
                f"Event added to calendar:\n\n"
                f"Title: {event['title']}\n"
                f"Start: {event['start_time']}\n"
                f"Duration: {event['duration']} minutes\n"
                f"Meeting URL: {event['meeting_url']}\n"
                f"Meeting ID: {event['meeting_id']}\n"
                f"Description: {event['description']}"
            ),
            "event": event
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to add event to calendar: {str(e)}"
        }

def list_calendar_events(date: Optional[str] = None) -> Dict[str, Any]:
    """List calendar events, optionally filtered by date.
    
    Args:
        date: Optional date filter (YYYY-MM-DD format)
        
    Returns:
        dict: Status and list of events
    """
    try:
        events = calendar_storage.list_events(date)
        
        if not events:
            return {
                "status": "success",
                "report": "No events found in calendar.",
                "events": []
            }

        events_summary = "\n\n".join([
            f"Event: {event['title']}\n"
            f"Start: {event['start_time']}\n"
            f"Duration: {event['duration']} minutes\n"
            f"Meeting URL: {event['meeting_url']}"
            for event in events
        ])

        return {
            "status": "success",
            "report": f"Found {len(events)} events:\n\n{events_summary}",
            "events": events
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to list calendar events: {str(e)}"
        } 