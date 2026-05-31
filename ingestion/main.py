import os
import json
import requests
import boto3
from datetime import datetime, timezone

TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("GITHUB_TOKEN no está configurado")


# -----------------------------
# S3 CONFIG
# -----------------------------

s3 = boto3.client("s3")
BUCKET_NAME = "event-driven-lakehouse-bronze"


# -----------------------------
# GITHUB API
# -----------------------------

def fetch_events_page(owner, repo, page=1, per_page=100):

    url = f"https://api.github.com/repos/{owner}/{repo}/events"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    params = {
        "page": page,
        "per_page": per_page
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def fetch_all_events(owner, repo):

    all_events = []

    for page in range(1, 4):  # max 300 events

        print(f"Fetching page {page}...")

        events = fetch_events_page(owner, repo, page, 100)

        print(f"Fetched {len(events)} events")

        if not events:
            break

        all_events.extend(events)

    return all_events


# -----------------------------
# S3 STREAMING UPLOAD
# -----------------------------

def build_s3_key(owner: str, repo: str) -> str:

    now = datetime.now(timezone.utc)

    return (
        f"bronze/github_events/"
        f"repo={owner}-{repo}/"
        f"year={now.year}/"
        f"month={now.month:02d}/"
        f"day={now.day:02d}/"
        f"events_{now.strftime('%Y%m%d_%H%M%S')}.jsonl"
    )


def upload_jsonl_to_s3(events, owner, repo):

    key = build_s3_key(owner, repo)

    # 🔥 streaming en memoria (NO file)
    jsonl_data = "\n".join(
        json.dumps(event) for event in events
    )

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=jsonl_data.encode("utf-8")
    )

    print(f"\nUploaded to s3://{BUCKET_NAME}/{key}")


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    owner = "apache"
    repo = "spark"

    events = fetch_all_events(owner, repo)

    print(f"\nTotal events fetched: {len(events)}")

    upload_jsonl_to_s3(events, owner, repo)