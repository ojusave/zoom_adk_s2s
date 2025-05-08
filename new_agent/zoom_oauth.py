import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_zoom_access_token() -> str:
    """Gets an OAuth access token for the Zoom API."""
    client_id = os.getenv('ZOOM_CLIENT_ID')
    client_secret = os.getenv('ZOOM_CLIENT_SECRET')
    account_id = os.getenv('ZOOM_ACCOUNT_ID')
    
    if not all([client_id, client_secret, account_id]):
        raise ValueError("Missing required Zoom credentials in .env file")
    
    auth_string = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_string}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'account_credentials',
        'account_id': account_id
    }
    
    response = requests.post(
        'https://zoom.us/oauth/token',
        headers=headers,
        data=data
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.text}")
    
    return response.json()['access_token'] 