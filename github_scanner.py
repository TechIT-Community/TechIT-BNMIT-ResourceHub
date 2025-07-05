import requests
from app import db, Resource, app  # Make sure app.py is in the same folder
import time

# Base API URL of your GitHub repo (change if needed)
GITHUB_API_REPO = "https://api.github.com/repos/TechIT-Community/TechIT-BNMIT-ResourceHub/contents/"

# ✅ Parse GitHub file path into metadata
def parse_github_path(path):
    parts = path.strip("/").split("/")

    # Safely assign metadata, or fallback to defaults
    department = parts[0] if len(parts) > 0 else "Unknown"
    semester = parts[1] if len(parts) > 1 else "Unknown"
    subject = parts[2] if len(parts) > 2 else "Unknown"
    type_ = parts[3] if len(parts) > 3 else "misc"
    title = parts[-1] if len(parts) > 0 else "Untitled"

    return {
        "department": department,
        "semester": semester,
        "subject": subject,
        "type": type_,
        "title": title
    }

# 🔁 Recursively scan GitHub directory
def scan_github_folder(api_url):
    response = requests.get(api_url)
    if response.status_code != 200:
        print(f"⚠️ Failed to fetch: {api_url}")
        return []

    files = response.json()
    all_resources = []

    for file in files:
        print(f"➡️ Found: {file['path']} ({file['type']})")

        if file["type"] == "file":
            if file["name"].startswith(".") or file["name"].endswith(".md"):
                continue  # Skip hidden files and markdown
            meta = parse_github_path(file["path"])
            resource = Resource(
                title=meta["title"],
                subject=meta["subject"],
                semester=meta["semester"],
                department=meta["department"],
                type=meta["type"],
                source="github",
                link=file["html_url"]
            )
            print(f"📦 Prepared: {meta['title']}")
            all_resources.append(resource)

        elif file["type"] == "dir":
            # Recurse into the subdirectory
            time.sleep(0.3)  # Respect GitHub API rate limits
            all_resources.extend(scan_github_folder(file["url"]))

    return all_resources

# 🧠 Run inside Flask app context
with app.app_context():
    try:
        print("🔄 Scanning GitHub repository...")
        resources = scan_github_folder(GITHUB_API_REPO)

        for r in resources:
            db.session.add(r)

        db.session.commit()
        print(f"✅ Inserted {len(resources)} GitHub resource(s) into the database.")

    except Exception as e:
        print("❌ Error during insertion:", e)
        db.session.rollback()
