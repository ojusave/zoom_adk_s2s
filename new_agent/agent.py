from google.adk.agents import Agent, SequentialAgent, LlmAgent
from .gmail import check_emails, mark_as_read
from .zoom import create_zoom_meeting
from .calendar import add_to_calendar, list_calendar_events
from .meeting_agent import check_upcoming_meetings, open_zoom_url
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

# Meeting Scheduler Agent - Creates Zoom meetings when needed
meeting_scheduler_agent = LlmAgent(
    name="MeetingSchedulerAgent",
    model="gemini-2.0-flash",
    description="Creates Zoom meetings based on email analysis",
    instruction="""You are a meeting scheduler.
Based on the email analysis, if a meeting is required:

1. Extract meeting details from the analysis
2. For urgent meetings:
   - Set start_time to empty string (the Zoom API will handle scheduling 5 mins from now)
   - Set duration to 30 minutes by default

3. For normal meetings:
   - Set start_time to a future time in format: YYYY-MM-DD HH:MM:SS
   - Use the duration from MEETING_DETAILS

4. Create a Zoom meeting with:
   - Topic from MEETING_DETAILS
   - Duration as determined above
   - Start time as determined above
   - Description from MEETING_DETAILS

If the email analysis shows:
MEETING_REQUIRED: no
Then do nothing and return "No meeting required."

Email analysis:
{email_analysis}
""",
    tools=[create_zoom_meeting],
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
   "✅ Meeting added to calendar successfully."

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
    tools=[check_upcoming_meetings, open_zoom_url],
    output_key="meeting_join_result"
)

# Create the sequential workflow
email_workflow = SequentialAgent(
    name="EmailWorkflowAgent",
    description="Manages the email checking, meeting scheduling, calendar management, and meeting joining workflow",
    sub_agents=[
        email_checker_agent,
        email_analyzer_agent,
        meeting_scheduler_agent,
        calendar_manager_agent,
        meeting_joiner_agent
    ]
)

# Set as the root agent
root_agent = email_workflow 