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
- Zoom Account with Server-to-Server OAuth app
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

### 1. Zoom Server-to-Server OAuth Setup

1. Log in to your Zoom Developer Account at https://marketplace.zoom.us/
2. Navigate to "Develop" > "Build App"
3. Click "Create" and select "Server-to-Server OAuth"
4. Fill in the app information:
   - App Name: Your app name
   - App Type: Server-to-Server OAuth
   - Company Name: Your company name
   - Developer Contact Information: Your email
5. Under "Scopes", add the following **granular scopes** for meeting management:
   - `meeting:write:meeting` — Create, update, and delete meetings
   - `meeting:write:meeting:admin` — Create, update, and delete meetings as admin
   - `meeting:read:meeting` — View meeting details
   - `meeting:read:meeting:admin` — View meeting details as admin

   (Reference: [Zoom API documentation](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/))

6. Save and activate your app
7. Note down your:
   - Client ID
   - Client Secret
   - Account ID (found in your Zoom account settings)

### 2. Google Cloud Project Setup

1. Go to the Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google ADK API
   - Cloud Natural Language API
4. Create a service account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Grant the following roles:
     - ADK API User
     - Cloud Natural Language API User
5. Create and download a JSON key file for the service account

### 3. Environment Configuration

1. Create a `.env` file in the project root:
```bash
touch .env
```

2. Add the following variables to your `.env` file:
```env
# Zoom Credentials
ZOOM_CLIENT_ID=your_client_id_here
ZOOM_CLIENT_SECRET=your_client_secret_here
ZOOM_ACCOUNT_ID=your_account_id_here

# Google Cloud Credentials
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT=your_project_id

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=1
LOG_LEVEL=INFO
```

3. Set up the Google credentials:
```bash
# For Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"

# For Windows (PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

### 4. Testing Environment Setup

1. Create a test configuration file `config.test.py`:
```python
TEST_CONFIG = {
    'ZOOM_CLIENT_ID': 'test_client_id',
    'ZOOM_CLIENT_SECRET': 'test_client_secret',
    'ZOOM_ACCOUNT_ID': 'test_account_id',
    'GOOGLE_APPLICATION_CREDENTIALS': 'path/to/test/credentials.json'
}
```

2. Create a test `.env.test` file:
```env
ZOOM_CLIENT_ID=test_client_id
ZOOM_CLIENT_SECRET=test_client_secret
ZOOM_ACCOUNT_ID=test_account_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/test/credentials.json
FLASK_ENV=testing
FLASK_DEBUG=0
LOG_LEVEL=DEBUG
```

## Project Structure

```
zoom_adk_s2s/
├── new_agent/
│   ├── __init__.py
│   ├── agent.py          # Google ADK agent implementation
│   ├── main.py          # Application entry point
│   ├── zoom.py          # Zoom API integration
│   └── zoom_oauth.py    # OAuth authentication handling
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_zoom.py
│   └── test_oauth.py
├── config/
│   ├── __init__.py
│   ├── config.py
│   └── config.test.py
├── .env
├── .env.test
├── requirements.txt
└── README.md
```

## Usage

### Starting the Application

1. Ensure your environment is properly configured:
```bash
# Check if .env file exists
ls -la .env

# Verify environment variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('ZOOM_CLIENT_ID:', os.getenv('ZOOM_CLIENT_ID'))"
```

2. Start the application:
```bash
python new_agent/main.py
```

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

## Testing

### Testing with the ADK Web CLI

All agent testing is performed using the ADK Web interface, which you can launch directly from your terminal.

#### Steps to Test Your Agent

1. **Activate your virtual environment (if not already active):**
   ```bash
   source venv/bin/activate
   ```

2. **Start the ADK Web interface:**
   ```bash
   adk web
   ```
   This command will launch the ADK web UI in your browser, allowing you to interactively test your agent.

3. **Use the ADK Web UI:**
   - Select your agent.
   - Enter natural language prompts (e.g., "Create a meeting tomorrow at 2pm").
   - Observe and validate the agent's responses.
   - Test various scenarios, edge cases, and error handling.

4. **Review logs and analytics in the web UI.**

5. **Iterate:**
   - Make code changes locally as needed.
   - Restart `adk web` to reload your agent and repeat testing.

> **Note:** The `adk web` command is the primary and recommended way to validate your agent's behavior.

## Troubleshooting

### 1. Authentication Issues

1. Check Zoom Credentials:
```bash
# Verify Zoom credentials
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('ZOOM_CLIENT_ID:', os.getenv('ZOOM_CLIENT_ID'))"
```

2. Check Google Credentials:
```bash
# Verify Google credentials
python -c "import os; print('GOOGLE_APPLICATION_CREDENTIALS:', os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))"
```



