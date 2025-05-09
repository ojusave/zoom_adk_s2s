from .agent import root_agent

def handle_zoom_request(request: str) -> str:
    """Handle a Zoom meeting request and return the response."""
    try:
        response = root_agent.run(request)
        return response.get("meeting_result", "No response from agent")
    except Exception as e:
        return f"Error processing request: {str(e)}"

if __name__ == "__main__":
    # Example usage
    request = input("Enter your Zoom meeting request: ")
    response = handle_zoom_request(request)
    print(response)
