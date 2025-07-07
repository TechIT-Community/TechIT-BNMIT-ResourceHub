import os
import io
import base64
import re
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
from dotenv import load_dotenv
load_dotenv()


# ---------------------------
# CONFIGURATION
# ---------------------------
SCOPES = ['https://www.googleapis.com/auth/drive.file']
ROOT_FOLDER_ID = '1Le_C3BJGhWXzOJO8XJcM4DmGzJwWZcqc'  # Replace with actual Drive folder ID
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set in environment
GITHUB_REPO = "TechIT-Community/TechIT-BNMIT-ResourceHub"
GITHUB_API = "https://api.github.com"

# ---------------------------
# AUTHENTICATE GOOGLE DRIVE
# ---------------------------
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

# ---------------------------
# CLASSIFY FILE TYPE
# ---------------------------
def classify_file(filename):
    extension = filename.lower().split('.')[-1]
    code_exts = {'py', 'java', 'c', 'cpp', 'js', 'ts', 'html', 'css'}
    binary_exts = {'pdf', 'jpg', 'jpeg', 'png', 'docx'}

    if extension in code_exts:
        return 'code'
    elif extension in binary_exts:
        return 'binary'
    else:
        return 'other'

# ---------------------------
# FOLDER MANAGEMENT
# ---------------------------
def ensure_folder(service, name, parent_id):
    query = f"'{parent_id}' in parents and name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    result = service.files().list(q=query, fields="files(id)").execute()
    folders = result.get("files", [])
    if folders:
        return folders[0]['id']
    metadata = {
        'name': name,
        'parents': [parent_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=metadata, fields='id').execute()
    return folder.get('id')

# ---------------------------
# UPLOAD TO GOOGLE DRIVE
# ---------------------------
def upload_to_drive(file_bytes, filename, department, semester, subject, type_label):
    service = authenticate_drive()

    dep_id = ensure_folder(service, department, ROOT_FOLDER_ID)
    sem_id = ensure_folder(service, semester, dep_id)
    subj_id = ensure_folder(service, subject, sem_id)
    type_id = ensure_folder(service, type_label, subj_id)

    file_metadata = {
        'name': filename,
        'parents': [type_id]
    }
    media = MediaIoBaseUpload(file_bytes, mimetype='application/octet-stream')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    return file.get('webViewLink')

# ---------------------------
# CREATE GITHUB PR
# ---------------------------
def create_github_pr(file_bytes, filename, department, semester, subject, type_label):
    if not GITHUB_TOKEN:
        raise Exception("GitHub token not set in environment")

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # 1. Get default branch
    repo_url = f"{GITHUB_API}/repos/{GITHUB_REPO}"
    repo_data = requests.get(repo_url, headers=headers).json()
    default_branch = repo_data.get("default_branch", "main")

    # 2. Create a new branch from main
    ref_url = f"{GITHUB_API}/repos/{GITHUB_REPO}/git/ref/heads/{default_branch}"
    base_sha = requests.get(ref_url, headers=headers).json()['object']['sha']
    branch_name = f"upload-{filename.replace('.', '-')}-{os.urandom(4).hex()}"
    branch_ref_url = f"{GITHUB_API}/repos/{GITHUB_REPO}/git/refs"
    requests.post(branch_ref_url, headers=headers, json={
        "ref": f"refs/heads/{branch_name}",
        "sha": base_sha
    })

    # 3. Commit file to branch
    content = base64.b64encode(file_bytes.read()).decode('utf-8')
    github_path = f"{department}/{semester}/{subject}/{type_label}/{filename}"
    commit_url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{github_path}"
    commit_res = requests.put(commit_url, headers=headers, json={
        "message": f"Add {filename} via contribution upload",
        "content": content,
        "branch": branch_name
    })

    if commit_res.status_code not in (200, 201):
        raise Exception(f"GitHub commit failed: {commit_res.text}")

    # 4. Create Pull Request
    pr_url = f"{GITHUB_API}/repos/{GITHUB_REPO}/pulls"
    pr_res = requests.post(pr_url, headers=headers, json={
        "title": f"Add {filename} to {subject}",
        "head": branch_name,
        "base": default_branch,
        "body": f"Uploaded via Streamlit by contributor to {department}/{semester}/{subject}"
    })

    if pr_res.status_code not in (200, 201):
        raise Exception(f"GitHub PR failed: {pr_res.text}")

    return pr_res.json()['html_url']
