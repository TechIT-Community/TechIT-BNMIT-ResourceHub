# -----------------------------
# github_scanner.py
# -----------------------------
import requests
import os
from datetime import datetime
from db import Resource, SessionLocal

GITHUB_API_REPO = "https://api.github.com/repos/TechIT-Community/TechIT-BNMIT-ResourceHub/contents/CSE"
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.jpg', '.jpeg'}

def is_allowed(filename):
    return os.path.splitext(filename.lower())[1] in ALLOWED_EXTENSIONS

def parse_metadata(path):
    parts = path.strip("/").split("/")
    return {
        "department": parts[0] if len(parts) > 0 else "Unknown",
        "semester": parts[1] if len(parts) > 1 else "Unknown",
        "subject": parts[2] if len(parts) > 2 else "Unknown",
        "type": parts[3] if len(parts) > 3 else "misc",
        "title": parts[-1]
    }

def crawl_github(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        items = r.json()
    except:
        return []

    resources = []

    for item in items:
        path = item['path']
        name = item['name']
        html_url = item['html_url']
        meta = parse_metadata(path)

        if item['type'] == 'dir':
            # Index the folder itself
            resources.append({
                **meta,
                "link": html_url,
                "last_updated": datetime.utcnow(),
                "is_folder": True,
                "type": "folder"
            })
            # Recurse inside
            resources.extend(crawl_github(item['url']))

        elif item['type'] == 'file' and is_allowed(name):
            resources.append({
                **meta,
                "link": html_url,
                "last_updated": datetime.utcnow(),
                "is_folder": False
            })

    return resources

def run_github_sync():
    session = SessionLocal()
    existing = {r.link: r for r in session.query(Resource).filter_by(source="github").all()}
    found = crawl_github(GITHUB_API_REPO)

    inserted = updated = 0
    for f in found:
        link = f['link']
        existing_entry = existing.get(link)

        if existing_entry:
            # Update only if something has changed
            if existing_entry.title != f['title'] or existing_entry.is_folder != f['is_folder']:
                existing_entry.title = f['title']
                existing_entry.subject = f['subject']
                existing_entry.semester = f['semester']
                existing_entry.department = f['department']
                existing_entry.type = f['type']
                existing_entry.last_updated = f['last_updated']
                existing_entry.is_folder = f['is_folder']
                updated += 1
        else:
            session.add(Resource(
                title=f['title'],
                subject=f['subject'],
                semester=f['semester'],
                department=f['department'],
                type=f['type'],
                source="github",
                link=f['link'],
                last_updated=f['last_updated'],
                is_folder=f['is_folder']
            ))
            inserted += 1

    session.commit()
    session.close()
    print(f"📦 GitHub sync → Inserted: {inserted}, Updated: {updated}")
