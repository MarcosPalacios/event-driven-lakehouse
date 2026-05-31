import json
import logging
import os
import sys
from datetime import datetime, timezone

import boto3
import requests

TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise ValueError("GITHUB_TOKEN no está configurado")


# -----------------------------
# LOGGING
# -----------------------------

logger = logging.getLogger("ingestion")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.handlers = [handler]


def utc_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(event: str, repo: str, **metadata) -> None:
    payload = {
        "timestamp": utc_iso_timestamp(),
        "event": event,
        "repo": repo,
    }
    payload.update(metadata)
    logger.info(json.dumps(payload, default=str))


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

        events = fetch_events_page(owner, repo, page, 100)
        log_event(
            event="github_page_fetched",
            repo=f"{owner}/{repo}",
            page=page,
            events_fetched=len(events),
        )

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

    log_event(
        event="s3_upload_start",
        repo=f"{owner}/{repo}",
        bucket=BUCKET_NAME,
        key=key,
        records=len(events),
    )

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=jsonl_data.encode("utf-8")
    )

    log_event(
        event="s3_upload_complete",
        repo=f"{owner}/{repo}",
        bucket=BUCKET_NAME,
        key=key,
        records=len(events),
    )


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    owner = "apache"
    repo = "spark"
    repo_name = f"{owner}/{repo}"

    log_event(event="pipeline_start", repo=repo_name)

    events = fetch_all_events(owner, repo)
    log_event(
        event="github_fetch_complete",
        repo=repo_name,
        total_events=len(events),
    )

    upload_jsonl_to_s3(events, owner, repo)