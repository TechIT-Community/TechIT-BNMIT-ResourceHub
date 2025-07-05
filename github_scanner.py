import requests
from app import db, Resource, app  # Reuse the Flask app context and model

# 📁 Base GitHub API URL (change if your repo or structure changes)
GITHUB_API_REPO = "https://api.github.com/repos/TechIT-Community/TechIT-BNMIT-ResourceHub/contents/"

# 🧠 Custom logic to extract info from path
def parse_github_path(path):
    parts = path.strip("/").split("/")
    if len(parts) >= 2:
        return {
            "department": parts[0],
            "semester": parts[1],
            "subject": parts[2],
            "type": parts[3],
            "title": parts[-1]
        }
    return {}

# 🔁 Recursively scan folders
def scan_github_folder(api_url):
    response = requests.get(api_url)
    if response.status_code != 200:
        print(f"⚠️ Failed to fetch: {api_url}")
        return []

    files = response.json()
    all_resources = []

    for file in files:
        if file["type"] == "file":
            meta = parse_github_path(file["path"])
            if meta:
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
            # Recurse into subdirectory
            all_resources.extend(scan_github_folder(file["url"]))

    return all_resources

# 🧩 Load data into DB
with app.app_context():
    try:
        print("🔄 Scanning GitHub repo...")
        resources = scan_github_folder(GITHUB_API_REPO)

        for r in resources:
            db.session.add(r)

        db.session.commit()
        print(f"✅ {len(resources)} GitHub resources inserted into database.")
    except Exception as e:
        print("❌ Error during insertion:", e)
        db.session.rollback()
