# -----------------------------
# drive_scanner.py
# -----------------------------
import os
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from db import Resource, SessionLocal

# 📁 Root folder ID to start scanning
ROOT_FOLDER_ID = "1Le_C3BJGhWXzOJO8XJcM4DmGzJwWZcqc"

# 🎯 File types to index
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.docx'}

# 🔐 Google Drive API scopes
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


def is_allowed(name):
    _, ext = os.path.splitext(name.lower())
    return ext in ALLOWED_EXTENSIONS


def traverse_drive(service, folder_id, path="", collected=[]):
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, mimeType, modifiedTime, webViewLink)",
    ).execute()

    for item in results.get('files', []):
        item_path = f"{path}/{item['name']}".strip("/")
        is_folder = item['mimeType'] == 'application/vnd.google-apps.folder'
        modified = datetime.fromisoformat(item['modifiedTime'].replace("Z", "+00:00"))

        if is_folder:
            # 📁 Index the folder itself
            collected.append({
                "title": item['name'],
                "subject": "Unknown",
                "semester": "Unknown",
                "department": "Unknown",
                "type": "folder",
                "source": "drive",
                "link": item['webViewLink'],
                "last_updated": modified,
                "is_folder": True
            })
            traverse_drive(service, item['id'], item_path, collected)
        else:
            if is_allowed(item['name']):
                collected.append({
                    "title": item['name'],
                    "subject": "Unknown",
                    "semester": "Unknown",
                    "department": "Unknown",
                    "type": os.path.splitext(item['name'])[1][1:].upper(),
                    "source": "drive",
                    "link": item['webViewLink'],
                    "last_updated": modified,
                    "is_folder": False
                })

    return collected


def run_drive_sync():
    print("🔐 Authenticating with Google Drive...")
    service = authenticate_drive()
    print("🔍 Crawling Drive...")

    session = SessionLocal()
    files = traverse_drive(service, ROOT_FOLDER_ID)
    existing = {r.link: r for r in session.query(Resource).filter_by(source="drive").all()}
    current_links = set()

    inserted = updated = 0

    for f in files:
        link = f['link']
        current_links.add(link)
        existing_entry = existing.get(link)

        if existing_entry:
            db_time = existing_entry.last_updated.replace(tzinfo=timezone.utc)
            if db_time < f['last_updated']:
                existing_entry.title = f['title']
                existing_entry.type = f['type']
                existing_entry.last_updated = f['last_updated']
                existing_entry.is_folder = f['is_folder']
                updated += 1
        else:
            session.add(Resource(**f))
            inserted += 1

    # Optional: delete stale entries
    for link in existing:
        if link not in current_links:
            session.delete(existing[link])

    session.commit()
    session.close()
    print(f"📁 Drive sync → Inserted: {inserted}, Updated: {updated}, Deleted: {len(existing) - len(current_links)}")
