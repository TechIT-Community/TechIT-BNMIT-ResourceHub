import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from app import db, Resource, app

# ✅ Folder ID to scan from
ROOT_FOLDER_ID = "1Le_C3BJGhWXzOJO8XJcM4DmGzJwWZcqc"

# ✅ Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.docx'}

# ✅ Google API Scopes
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


def is_allowed_file(name):
    _, ext = os.path.splitext(name.lower())
    return ext in ALLOWED_EXTENSIONS


def traverse_drive(service, folder_id, collected=[]):
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, mimeType, modifiedTime, webViewLink)",
    ).execute()

    for item in results.get('files', []):
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            traverse_drive(service, item['id'], collected)
        else:
            if is_allowed_file(item['name']):
                collected.append(item)

    return collected


def sync_drive_to_db(service):
    print("🔍 Indexing Drive contents...")
    files = traverse_drive(service, ROOT_FOLDER_ID)

    # Load existing file IDs from the database
    existing_files = {r.link: r for r in Resource.query.filter_by(source="drive").all()}
    current_links = set()

    inserted, updated = 0, 0

    for item in files:
        file_link = item['webViewLink']
        current_links.add(file_link)

        if file_link in existing_files:
            # Check if update is needed
            resource = existing_files[file_link]
            drive_modified = datetime.fromisoformat(item['modifiedTime'].replace("Z", "+00:00"))
            if resource.last_updated < drive_modified:
                resource.title = item['name']
                resource.last_updated = drive_modified
                db.session.commit()
                updated += 1
        else:
            # New entry
            resource = Resource(
                title=item['name'],
                subject="Unknown",
                semester="Unknown",
                department="Unknown",
                type=os.path.splitext(item['name'])[1][1:].upper(),
                source="drive",
                link=file_link,
                last_updated=datetime.fromisoformat(item['modifiedTime'].replace("Z", "+00:00"))
            )
            db.session.add(resource)
            db.session.commit()
            inserted += 1

    # Delete stale entries
    for link in existing_files:
        if link not in current_links:
            db.session.delete(existing_files[link])
    db.session.commit()

    print(f"✅ Sync complete. Inserted: {inserted}, Updated: {updated}, Deleted: {len(existing_files) - len(current_links)}")


# 🧠 Run the sync process
with app.app_context():
    try:
        print("🔐 Authenticating with Google Drive...")
        service = authenticate_drive()
        sync_drive_to_db(service)
    except Exception as e:
        print("❌ Error during Drive sync:", e)
        db.session.rollback()
