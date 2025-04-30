from typing import Dict, Any
from datetime import datetime

def get_mock_emails() -> Dict[str, Any]:
    """Get mock emails from our dummy email database.
    
    Returns:
        dict: A dictionary containing mock email data
    """
    return {
        "status": "success",
        "emails": [
            {
                "id": "1",
                "subject": "Urgent: Need to schedule a meeting now",
                "sender": "manager@company.com",
                "content": "We need to discuss the project status ASAP. Please schedule a meeting today.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "priority": "high",
                "is_read": False
            },
            {
                "id": "2",
                "subject": "Important task needs to be delivered",
                "sender": "team@company.com",
                "content": "The client is expecting the deliverables by EOD. Please review and submit.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "priority": "high",
                "is_read": False
            },
            {
                "id": "3",
                "subject": "You've won a prize! Claim now!!!",
                "sender": "unknown@suspicious.com",
                "content": "Congratulations! You've been selected to receive a special prize...",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "priority": "low",
                "is_read": False,
                "spam_probability": 0.95
            }
        ]
    }

def check_emails() -> Dict[str, Any]:
    """Check for new emails and return them with appropriate status.
    
    Returns:
        dict: Email check results with status and email data
    """
    try:
        emails = get_mock_emails()
        unread_count = sum(1 for email in emails["emails"] if not email["is_read"])
        urgent_count = sum(1 for email in emails["emails"] if email["priority"] == "high")
        
        return {
            "status": "success",
            "report": f"You have {unread_count} unread emails, {urgent_count} are urgent.",
            "emails": emails["emails"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }

def mark_as_read(email_id: str) -> Dict[str, Any]:
    """Mark an email as read (mock function).
    
    Args:
        email_id: The ID of the email to mark as read
        
    Returns:
        dict: Status of the operation
    """
    return {
        "status": "success",
        "report": f"Email {email_id} marked as read"
    } 