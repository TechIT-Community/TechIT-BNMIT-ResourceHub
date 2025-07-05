import requests
from app import db, Resource, app
from datetime import datetime
import os

# 🔗 Base GitHub repo content API URL
GITHUB_API_REPO = "https://api.github.com/repos/TechIT-Community/TechIT-BNMIT-ResourceHub/contents/"

# 📁 Allowed extensions (easy to extend)
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.docx'}

def is_allowed_file(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS

# 🔍 Extract metadata from path
def parse_github_path(path):
    parts = path.strip("/").split("/")
    if len(parts) >= 2:
        return {
            "department": parts[0] if len(parts) > 0 else "Unknown",
            "semester": parts[1] if len(parts) > 1 else "Unknown",
            "subject": parts[2] if len(parts) > 2 else "Unknown",
            "type": parts[3] if len(parts) > 3 else "misc",
            "title": parts[-1],
        }
    return {}

# 🔁 Recursively walk repo contents
def scan_github_folder(api_url):
    response = requests.get(api_url)
    files = response.json()
    all_resources = []

    for file in files:
        print(f"📄 Found: {file['path']} ({file['type']})")

    for file in files:
        if file["type"] == "file" and is_allowed_file(file["name"]):
            meta = parse_github_path(file["path"])
            if meta:
                all_resources.append({
                    **meta,
                    "link": file["html_url"],
                    "updated_at": file.get("git_url", "")  # Used as pseudo-ID
                })
        elif file["type"] == "dir":
            all_resources.extend(scan_github_folder(file["url"]))



    return all_resources

# 🧠 Insert or update records smartly
def sync_to_database(resources):
    existing_links = {r.link: r for r in Resource.query.all()}
    inserted = 0
    updated = 0

    for r in resources:
        existing = existing_links.get(r["link"])
        if existing:
            if existing.title != r["title"]:
                existing.title = r["title"]
                existing.subject = r["subject"]
                existing.semester = r["semester"]
                existing.department = r["department"]
                existing.type = r["type"]
                existing.last_updated = datetime.utcnow()
                updated += 1
        else:
            new_resource = Resource(
                title=r["title"],
                subject=r["subject"],
                semester=r["semester"],
                department=r["department"],
                type=r["type"],
                source="github",
                link=r["link"],
                last_updated=datetime.utcnow()
            )
            db.session.add(new_resource)
            inserted += 1

    db.session.commit()
    return inserted, updated

# 🚀 Main entry
if __name__ == "__main__":
    with app.app_context():
        print("🔄 Scanning GitHub repo...")
        try:
            resources = scan_github_folder(GITHUB_API_REPO)
            inserted, updated = sync_to_database(resources)
            print(f"✅ Sync complete. Inserted: {inserted}, Updated: {updated}")
        except Exception as e:
            db.session.rollback()
            print("❌ Error during GitHub scan:", e)
