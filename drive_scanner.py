from app import db, Resource, app
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Set up credentials and Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Replace with your path

FOLDER_ID = '1Le_C3BJGhWXzOJO8XJcM4DmGzJwWZcqc'  # Replace with actual

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

def list_files(folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    results = drive_service.files().list(
        q=query,
        fields="files(id, name, mimeType, webViewLink, parents)").execute()
    return results.get('files', [])

def parse_drive_file(file):
    # Assume file is inside structure like: CSE > Semester 4 > Subject
    return {
        "title": file['name'],
        "subject": "Unknown",
        "semester": "Unknown",
        "department": "Unknown",
        "type": "Unknown",
        "source": "drive",
        "link": file['webViewLink']
    }

with app.app_context():
    print("🔄 Scanning Google Drive...")
    files = list_files(FOLDER_ID)
    resources = []

    for f in files:
        meta = parse_drive_file(f)
        resource = Resource(**meta)
        resources.append(resource)

    for r in resources:
        db.session.add(r)
    db.session.commit()
    print(f"✅ Inserted {len(resources)} Drive files into the database.")
