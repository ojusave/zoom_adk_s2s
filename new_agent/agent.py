from google.adk.agents import Agent, SequentialAgent, LlmAgent
from .gmail import check_emails, mark_as_read
from .zoom import (
    create_zoom_meeting, update_zoom_meeting, delete_zoom_meeting,
    get_zoom_meeting, list_zoom_meetings, start_zoom_meeting, join_zoom_meeting,
    open_zoom_url
)
from .calendar import add_to_calendar, list_calendar_events
from datetime import datetime, timedelta

# Email Checker Agent - Handles checking for new emails
email_checker_agent = LlmAgent(
    name="EmailCheckerAgent",
    model="gemini-2.0-flash",
    description="Checks for new emails and provides a summary",
    instruction="""You are an email checking assistant.
Your task is to check for new emails and provide a clear summary of what you find.
Focus on urgent and important emails, and flag any potential spam.
""",
    tools=[check_emails],
    output_key="email_check_result"
)

# Email Analyzer Agent - Analyzes emails and determines if meetings are needed
email_analyzer_agent = LlmAgent(
    name="EmailAnalyzerAgent",
    model="gemini-2.0-flash",
    description="Analyzes emails and identifies meeting requirements",
    instruction="""You are an email analysis assistant.
Based on the email check results, you should:
1. Identify if any emails require scheduling a meeting
2. Extract meeting requirements (topic, urgency)
3. Flag important tasks and deadlines
4. Warn about potential spam

Use the following format:
MEETING_REQUIRED: [yes/no]
URGENCY: [urgent/normal]
MEETING_DETAILS: {
    "topic": "Meeting topic here",
    "description": "Brief description of meeting purpose",
    "duration": 30
}
IMPORTANT: [List important items]
SUSPICIOUS: [List suspicious items]

For urgent meetings:
- Set URGENCY to "urgent" if the email mentions immediate, urgent, or ASAP meetings
- Set URGENCY to "normal" for regular meetings

Email check results:
{email_check_result}
""",
    output_key="email_analysis"
)

# Create the Zoom meeting agent
zoom_meeting_agent = LlmAgent(
    name="ZoomMeetingAgent",
    model="gemini-2.0-flash",
    description="Creates and manages Zoom meetings based on user prompts",
    instruction="""
You are a Zoom meeting assistant.
After creating, updating, deleting, or retrieving meeting information, respond with a clear, human-readable summary of the result.
Format your responses using Markdown with embedded links.

Use these exact formats for your responses. Each line must be on its own line with a blank line between sections:

For a new meeting:
Your meeting "MEETING_TOPIC" has been created for DATE at TIME 

Duration: DURATION minutes .

Meeting ID: MEETING_ID

[Click here to join](JOIN_URL)

[Click here to start the meeting as host](START_URL)


For an updated meeting:
The meeting "MEETING_TOPIC" has been updated. New time: DATE at TIME .

Duration: DURATION minutes .

Meeting ID: MEETING_ID

[Click here to join](JOIN_URL)

[Click here to start the meeting as host](START_URL)


For retrieving meeting details:
Meeting "MEETING_TOPIC"

Scheduled for: DATE at TIME

Duration: DURATION minutes

Status: MEETING_STATUS

Meeting ID: MEETING_ID

[Click here to join](JOIN_URL)


For listing meetings:
Found NUMBER meetings between START_DATE and END_DATE:

1. "MEETING_TOPIC_1" on DATE_1 at TIME_1
Meeting ID: MEETING_ID_1
[Join](JOIN_URL_1)

2. "MEETING_TOPIC_2" on DATE_2 at TIME_2
Meeting ID: MEETING_ID_2
[Join](JOIN_URL_2)

...


For a deleted meeting:
The meeting with ID MEETING_ID has been deleted.


For starting a meeting:
Opening meeting "MEETING_TOPIC" in a new tab...


For joining a meeting:
Opening meeting "MEETING_TOPIC" in a new tab...


For errors:
Error: ERROR_MESSAGE


Guidelines:
- Replace placeholders (like MEETING_TOPIC, DATE, etc.) with actual values from the API response
- Do not return JSON or code blocks unless explicitly requested
- Each sentence must be on its own line
- Add a blank line between different sections
- Do not use emojis
- Always interpret relative dates and times (like 'tomorrow 12 pm', 'next Monday at 3 pm') using the current date as context
- If the user says 'tomorrow', resolve it to the actual date for tomorrow
- Do not ask the user to clarify relative dates—always infer and use the correct date
- When the user asks to edit, delete, or get details of a meeting and does not specify a meeting ID, always use the most recently created or edited meeting from the session context
- Do not ask the user for the meeting ID if there is a recent meeting in context—just use it
- Always format URLs as Markdown links with descriptive text
- When the user says "start meeting" or "join meeting" followed by a meeting topic or ID, use the appropriate function to open the meeting in a new tab
""",
    tools=[
        create_zoom_meeting, update_zoom_meeting, delete_zoom_meeting,
        get_zoom_meeting, list_zoom_meetings, start_zoom_meeting, join_zoom_meeting
    ],
    output_key="meeting_result"
)

# Calendar Management Agent - Adds meetings to calendar
calendar_manager_agent = LlmAgent(
    name="CalendarManagerAgent",
    model="gemini-2.0-flash",
    description="Manages calendar entries for scheduled meetings",
    instruction="""You are a calendar management assistant.
When a meeting has been scheduled:

1. Check if the meeting_result contains a successful meeting creation:
   - Look for "status": "success" in the meeting_result
   - If not found or status is "error", return "No meeting to add to calendar."

2. If meeting was successfully created:
   - Extract meeting details from the meeting_result
   - Add to calendar ONLY ONCE
   - Return ONLY the calendar addition confirmation
   - DO NOT add multiple confirmations
   - DO NOT repeat the meeting details

3. Format your response as:
   "Meeting added to calendar successfully."

DO NOT:
- Add the same meeting multiple times
- Repeat the meeting details
- Provide additional commentary

Meeting result:
{meeting_result}
""",
    tools=[add_to_calendar, list_calendar_events],
    output_key="calendar_result"
)

# Meeting Joiner Agent - Joins meetings that are about to start
meeting_joiner_agent = LlmAgent(
    name="MeetingJoinerAgent",
    model="gemini-2.0-flash",
    description="Checks for and joins upcoming meetings",
    instruction="""You are a meeting attendance assistant.
After a meeting has been added to the calendar:

1. Check for any meetings starting in the next 5 minutes
2. If an urgent meeting is found:
   - Join the meeting using the Zoom URL
   - Confirm that you've joined
3. If no urgent meetings:
   - Simply respond "No immediate meetings to join."

Calendar result:
{calendar_result}
""",
    tools=[list_zoom_meetings, open_zoom_url],
    output_key="meeting_join_result"
)

# Create the sequential workflow
email_workflow = SequentialAgent(
    name="EmailWorkflowAgent",
    description="Manages the email checking, meeting scheduling, calendar management, and meeting joining workflow",
    sub_agents=[
        email_checker_agent,
        email_analyzer_agent,
        zoom_meeting_agent,
        calendar_manager_agent,
        meeting_joiner_agent
    ]
)

# Set as the root agent
root_agent = email_workflow 