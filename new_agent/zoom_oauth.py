import os
import requests
from flask import Flask, request, redirect, session, render_template_string, jsonify
from dotenv import load_dotenv
import json
from typing import Dict, Optional
import time
import threading
from queue import Queue
import webview
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# OAuth configuration
CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')
# Use environment variable for redirect URI, fallback to localhost for development
REDIRECT_URI = os.getenv('ZOOM_REDIRECT_URI')
if not REDIRECT_URI:
    logger.warning("ZOOM_REDIRECT_URI not set, using localhost for development")
    REDIRECT_URI = 'http://localhost:3000/oauth/callback'

AUTH_URL = 'https://zoom.us/oauth/authorize'
TOKEN_URL = 'https://zoom.us/oauth/token'

# Create Flask app for handling OAuth flow
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Store tokens in memory (in production, use a proper database)
tokens = {}
auth_complete = Queue()
window = None

# HTML template for the popup window
POPUP_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Zoom Authorization</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f5f5f5;
        }
        .container {
            text-align: center;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .success {
            color: #28a745;
        }
        .error {
            color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Zoom Authorization</h2>
        <p id="message">{{ message }}</p>
    </div>
    <script>
        // Close the popup after 1 second
        setTimeout(function() {
            window.close();
        }, 1000);
    </script>
</body>
</html>
"""

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

def start_oauth_server():
    """Start the Flask server for handling OAuth flow."""
    try:
        app.run(port=3000)
    except Exception as e:
        logger.error(f"Error starting OAuth server: {str(e)}")

def initiate_oauth_flow():
    """Start the OAuth flow and wait for completion."""
    global window
    
    # Start the OAuth server in a separate thread
    server_thread = threading.Thread(target=start_oauth_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Open the authorization URL in a popup window
    auth_url = get_authorization_url()
    logger.info(f"Opening popup window for Zoom authorization...")
    
    try:
        # Create a native window for the OAuth flow with specific options
        window = webview.create_window(
            'Zoom Authorization',
            auth_url,
            width=600,
            height=600,
            resizable=True,
            text_select=True,
            confirm_close=True,
            min_size=(400, 400)
        )
        
        def on_loaded():
            """Callback when the window is loaded."""
            pass
        
        def on_closed():
            """Callback when the window is closed."""
            if not tokens:
                auth_complete.put(False)
        
        window.events.loaded += on_loaded
        window.events.closed += on_closed
        
        # Start the webview in a non-blocking way
        webview.start(debug=True)
        
        logger.info("Please complete the authorization in the popup window.")
        # Wait for the authorization to complete
        result = auth_complete.get(timeout=300)  # 5 minute timeout
        if not result:
            raise Exception("Authorization was cancelled or failed")
        logger.info("Authorization completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during OAuth flow: {str(e)}")
        if window:
            try:
                window.destroy()
            except:
                pass
        raise
    finally:
        if window:
            try:
                window.destroy()
            except:
                pass

def get_zoom_access_token() -> str:
    """Get a valid access token, initiating OAuth flow if necessary."""
    if not tokens:
        logger.info("No tokens available. Initiating OAuth flow...")
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
        return render_template_string(POPUP_HTML, message="Authorization failed. Please try again."), 400
    
    try:
        token_data = exchange_code_for_token(code)
        tokens.update(token_data)
        tokens['expires_at'] = time.time() + token_data['expires_in']
        # Signal that authorization is complete
        auth_complete.put(True)
        # Close the window
        if window:
            try:
                window.destroy()
            except:
                pass
        return render_template_string(POPUP_HTML, message="Authorization successful! This window will close automatically.")
    except Exception as e:
        logger.error(f"Error in OAuth callback: {str(e)}")
        auth_complete.put(False)
        # Close the window on error
        if window:
            try:
                window.destroy()
            except:
                pass
        return render_template_string(POPUP_HTML, message=f"Error: {str(e)}"), 400

# Add a health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}) 