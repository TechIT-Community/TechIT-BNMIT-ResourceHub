import requests
from dotenv import load_dotenv
load_dotenv()
import os


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise Exception("GitHub token not found! Set it in your .env file.")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}
res = requests.get("https://api.github.com/repos/TechIT-Community/TechIT-BNMIT-ResourceHub", headers=headers)
print(res.status_code, res.json().get("default_branch"))
