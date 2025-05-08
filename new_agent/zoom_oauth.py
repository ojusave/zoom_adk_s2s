import os
import requests
import base64
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')
ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
TOKEN_URL = 'https://zoom.us/oauth/token'

def get_zoom_access_token() -> str:
    """Fetch a new Zoom S2S OAuth access token using account credentials."""
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "account_credentials",
        "account_id": ACCOUNT_ID
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code != 200:
        logger.error(f"Failed to get S2S access token: {response.text}")
        raise Exception(f"Failed to get S2S access token: {response.text}")
    token_data = response.json()
    return token_data['access_token'] 