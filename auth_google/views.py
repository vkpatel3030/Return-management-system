from django.shortcuts import render
import os
from django.shortcuts import redirect, render
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
import requests
import pathlib

load_dotenv()

def google_login(request):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=os.getenv("GOOGLE_SCOPES").split()
    )

    flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    request.session['state'] = state
    return redirect(auth_url)

def google_redirect(request):
    state = request.session.get('state')

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=os.getenv("GOOGLE_SCOPES").split(),
        state=state
    )
    flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    return redirect('home')

def drive_list(request):
    from google.oauth2.credentials import Credentials

    creds_data = request.session.get('credentials')
    if not creds_data:
        return redirect('google_login')

    creds = Credentials(
        token=creds_data['token'],
        refresh_token=creds_data['refresh_token'],
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret'],
        scopes=creds_data['scopes'],
    )

    headers = {"Authorization": f"Bearer {creds.token}"}
    response = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers)
    files = response.json().get("files", [])

    return render(request, "drive_files.html", {"files": files})
