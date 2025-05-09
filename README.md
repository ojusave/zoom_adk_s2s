# Zoom ADK S2S

A Python-based Zoom Agent built using Google ADK. This project provides a framework for building Zoom applications that can interact with the Zoom API using server-to-server OAuth authentication and Google's ADK (Application Development Kit) for AI-powered meeting management.

## Features

- Server-to-Server OAuth authentication with Zoom
- Google ADK integration for AI-powered meeting management
- Natural language processing for meeting scheduling
- Web-based interface using Flask and PyWebView
- Modular architecture for easy extension

## Prerequisites

- Python 3.8 or higher
- Zoom  Account with Server-to-Server OAuth app
- Google Cloud Project with ADK access
- Zoom Account ID, Client ID, and Client Secret

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd zoom_adk_s2s
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root with the following variables:
```
ZOOM_CLIENT_ID=your_client_id
ZOOM_CLIENT_SECRET=your_client_secret
ZOOM_ACCOUNT_ID=your_account_id
```

2. Configure your Google ADK credentials:
   - Set up a Google Cloud Project
   - Enable the ADK API
   - Configure authentication credentials

## Project Structure

```
zoom_adk_s2s/
├── new_agent/
│   ├── __init__.py
│   ├── agent.py          # Google ADK agent implementation
│   ├── main.py          # Application entry point
│   ├── zoom.py          # Zoom API integration
│   └── zoom_oauth.py    # OAuth authentication handling
├── requirements.txt
└── README.md
```

## Usage

### Starting the Application

1. Start the application:
```bash
python new_agent/main.py
```

2. The application will open a web interface where you can interact with the Zoom integration.

### Natural Language Commands

The application supports natural language commands for managing Zoom meetings. Here are some examples:

1. Create a meeting:
```
Create a meeting tomorrow at 2pm for team sync
```

2. List meetings:
```
Show my meetings for next week
```

3. Update a meeting:
```
Change the team sync meeting to 3pm tomorrow
```

4. Delete a meeting:
```
Delete the team sync meeting
```

5. Start/Join a meeting:
```
Start the team sync meeting
```

### Testing

1. Unit Tests:
```bash
python -m pytest tests/
```

2. Integration Tests:
```bash
python -m pytest tests/integration/
```

3. Manual Testing:
   - Test meeting creation with various time formats
   - Verify OAuth token refresh
   - Check error handling
   - Test natural language processing

### Common Test Cases

1. Meeting Creation:
   - Create meeting with specific time
   - Create meeting with relative time (tomorrow, next week)
   - Create meeting with duration
   - Create meeting with invalid time format

2. Meeting Management:
   - Update meeting time
   - Update meeting topic
   - Update meeting duration
   - Delete meeting
   - List meetings with date range

3. Authentication:
   - Test token refresh
   - Test invalid credentials
   - Test expired tokens

4. Error Handling:
   - Test invalid meeting IDs
   - Test network errors
   - Test API rate limits

## Dependencies

- google-api-python-client (>=2.108.0)
- google-auth-httplib2 (>=0.1.1)
- google-auth-oauthlib (>=1.1.0)
- requests (>=2.31.0)
- python-dotenv (>=1.0.0)
- flask (>=3.0.0)
- pywebview (>=4.4.1)

## Security

- Never commit your `.env` file or expose your credentials
- Keep your OAuth tokens secure
- Follow Zoom's security best practices
- Use environment variables for sensitive data
- Implement proper error handling and logging

## Troubleshooting

1. Authentication Issues:
   - Verify your Zoom credentials
   - Check token expiration
   - Ensure proper scopes are configured

2. Meeting Creation Issues:
   - Verify timezone settings
   - Check meeting duration limits
   - Validate meeting settings

3. API Rate Limits:
   - Implement proper rate limiting
   - Handle 429 responses
   - Use exponential backoff

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

## Support

For support, please [add your support contact information or process] 