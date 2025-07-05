import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from app import db, Resource, app
from datetime import datetime

# 🔧 Replace with your top-level Google Drive folder ID
ROOT_FOLDER_ID = "1Le_C3BJGhWXzOJO8XJcM4DmGzJwWZcqc"

# Only metadata permission required
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def authenticate_drive():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def scan_drive_flat(service, folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, mimeType, webViewLink)",
    ).execute()

    items = results.get('files', [])
    resources = []

    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            continue  # Skip subfolders for now

        # Skip code files or hidden
        if item['name'].startswith('.') or item['name'].endswith(('.py', '.cpp', '.exe')):
            continue

        resource = Resource(
            title=item['name'],
            subject="Unknown",        # Can be updated later
            semester="Unknown",
            department="Unknown",
            type="PDF" if item['name'].endswith('.pdf') else "File",
            source="drive",
            link=item['webViewLink'],
            last_updated=datetime.utcnow()
        )

        print(f"📄 {item['name']}")
        resources.append(resource)

    return resources

# 🔁 Run inside Flask context
with app.app_context():
    try:
        print("🔐 Authenticating with Google Drive...")
        service = authenticate_drive()
        print("🔍 Scanning flat folder contents...")
        resources = scan_drive_flat(service, ROOT_FOLDER_ID)

        for r in resources:
            db.session.add(r)

        db.session.commit()
        print(f"✅ Inserted {len(resources)} Drive file(s) into the database.")
    except Exception as e:
        print("❌ Error during Drive scan:", e)
        db.session.rollback()
