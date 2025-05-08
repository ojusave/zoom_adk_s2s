import os
import requests
from flask import Flask, request, redirect, session
from dotenv import load_dotenv
import json
from typing import Dict, Optional
import time
import webbrowser
import threading
from queue import Queue

# Load environment variables
load_dotenv()

# OAuth configuration
CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')
REDIRECT_URI = os.getenv('ZOOM_REDIRECT_URI', 'http://localhost:3000/oauth/callback')
AUTH_URL = 'https://zoom.us/oauth/authorize'
TOKEN_URL = 'https://zoom.us/oauth/token'

# Create Flask app for handling OAuth flow
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Store tokens in memory (in production, use a proper database)
tokens = {}
auth_complete = Queue()

def get_authorization_url() -> str:
    """Generate the authorization URL for user to click."""
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI
    }
    return f"{AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

def exchange_code_for_token(code: str) -> Dict:
    """Exchange authorization code for access token."""
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post(
        TOKEN_URL,
        data=data,
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.text}")
    
    return response.json()

def refresh_access_token(refresh_token: str) -> Dict:
    """Refresh the access token using refresh token."""
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    response = requests.post(
        TOKEN_URL,
        data=data,
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to refresh token: {response.text}")
    
    return response.json()

def initiate_oauth_flow():
    """Start the OAuth flow and wait for completion."""
    # Start the OAuth server in a separate thread
    server_thread = threading.Thread(target=start_oauth_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Open the authorization URL in the default browser
    auth_url = get_authorization_url()
    print(f"Opening browser for Zoom authorization...")
    webbrowser.open(auth_url)
    
    print("Please complete the authorization in your browser.")
    # Wait for the authorization to complete
    auth_complete.get()
    print("Authorization completed successfully!")

def get_zoom_access_token() -> str:
    """Get a valid access token, initiating OAuth flow if necessary."""
    if not tokens:
        print("No tokens available. Initiating OAuth flow...")
        initiate_oauth_flow()
    
    # Check if token needs refresh
    if tokens.get('expires_at', 0) < time.time():
        new_tokens = refresh_access_token(tokens['refresh_token'])
        tokens.update(new_tokens)
        tokens['expires_at'] = time.time() + new_tokens['expires_in']
    
    return tokens['access_token']

# Flask routes for OAuth flow
@app.route('/oauth/authorize')
def authorize():
    """Redirect user to Zoom authorization page."""
    return redirect(get_authorization_url())

@app.route('/oauth/callback')
def oauth_callback():
    """Handle the OAuth callback and store tokens."""
    code = request.args.get('code')
    if not code:
        return "Authorization failed", 400
    
    try:
        token_data = exchange_code_for_token(code)
        tokens.update(token_data)
        tokens['expires_at'] = time.time() + token_data['expires_in']
        # Signal that authorization is complete
        auth_complete.put(True)
        return "Authorization successful! You can close this window."
    except Exception as e:
        auth_complete.put(False)
        return f"Error: {str(e)}", 400

def start_oauth_server():
    """Start the Flask server for handling OAuth flow."""
    app.run(port=3000) 