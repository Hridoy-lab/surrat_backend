from google_auth_oauthlib.flow import InstalledAppFlow

def authenticate_google_drive(client_id, client_secret):
    # Define the scope
    scopes = ["https://www.googleapis.com/auth/drive.file"]


    client_config = {
        "installed": {
            "client_id": client_id,
            # Replace with your actual client ID
            "client_secret": client_secret,  # Replace with your actual client secret
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]  # Use a simple localhost redirect for this example
        }
    }

    # Create the flow using the client config
    flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)

    # Run the local server for authentication and authorization
    # Ensure 'access_type' is 'offline' to get a refresh token
    creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')

    # Print the credentials and the refresh token
    print("Credentials:", creds)
    print("Refresh Token:", creds.refresh_token)

    return creds
