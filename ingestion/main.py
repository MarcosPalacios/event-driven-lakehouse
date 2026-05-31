import json
import logging
import os
import sys
from datetime import datetime, timezone, timedelta

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

# Checkpointing bucket and key template
CHECKPOINT_BUCKET = "event-driven-lakehouse-bronze"


def build_checkpoint_key(owner: str, repo: str) -> str:
    return f"checkpoints/repo={owner}_{repo}.json"


from botocore.exceptions import ClientError


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


def _parse_iso_to_dt(ts: str) -> datetime:
    # GitHub timestamps end with Z (UTC); convert to +00:00 for fromisoformat
    if ts is None:
        raise ValueError("timestamp is None")
    if ts.endswith("Z"):
        ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)


def load_checkpoint(owner: str, repo: str) -> str:
    key = build_checkpoint_key(owner, repo)
    try:
        obj = s3.get_object(Bucket=CHECKPOINT_BUCKET, Key=key)
        body = obj["Body"].read().decode("utf-8")
        data = json.loads(body)
        last_run_at = data.get("last_run_at") or "1970-01-01T00:00:00Z"
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code in ("NoSuchKey", "404", "NoSuchBucket"):
            last_run_at = "1970-01-01T00:00:00Z"
        else:
            raise

    log_event(event="checkpoint_loaded", repo=f"{owner}/{repo}", last_run_at=last_run_at)
    return last_run_at


def save_checkpoint(owner: str, repo: str, last_run_at: str) -> None:
    key = build_checkpoint_key(owner, repo)
    payload = json.dumps({"last_run_at": last_run_at})

    s3.put_object(
        Bucket=CHECKPOINT_BUCKET,
        Key=key,
        Body=payload.encode("utf-8"),
        ContentType="application/json",
    )

    log_event(event="checkpoint_updated", repo=f"{owner}/{repo}", last_run_at=last_run_at)


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

    # Load checkpoint and filter events newer than last_run_at (with margin)
    last_run_at = load_checkpoint(owner, repo)
    last_run_dt = _parse_iso_to_dt(last_run_at)

    margin = timedelta(minutes=2)
    effective_cutoff = last_run_dt - margin

    filtered_events = []
    for ev in events:
        created_at = ev.get("created_at")
        if not created_at:
            continue
        try:
            created_dt = _parse_iso_to_dt(created_at)
        except Exception:
            continue

        if created_dt > effective_cutoff:
            filtered_events.append(ev)

    log_event(
        event="events_filtered",
        repo=repo_name,
        before=len(events),
        after=len(filtered_events),
        last_run_at=last_run_at,
    )

    if filtered_events:
        upload_jsonl_to_s3(filtered_events, owner, repo)

        # compute max created_at from ingested events and save checkpoint
        max_dt = max(_parse_iso_to_dt(e["created_at"]) for e in filtered_events)
        max_iso = max_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        save_checkpoint(owner, repo, max_iso)
    else:
        log_event(event="no_new_events", repo=repo_name, last_run_at=last_run_at)