# GitHub Events Ingestion Service (Bronze Layer)

## Overview

This module extracts GitHub events and writes raw batches to the Bronze layer.
It is the first stage of the pipeline and produces local JSONL files that can later be moved to S3.

## What it does

- Fetches repository events from GitHub using the `/repos/{owner}/{repo}/events` endpoint
- Handles pagination for up to 3 pages of 100 events
- Saves each batch as a JSONL file in `outputs/bronze/`
- Preserves the original event payload without transformation

## What it does not do

- No data cleanup or normalization
- No deduplication or record-level state management
- No schema enforcement
- No analytics-ready formatting

## Output

- Format: JSON Lines (`.jsonl`)
- Local folder: `outputs/bronze/`
- File naming: `github_events_YYYYMMDD_HHMMSS.jsonl`

Example line:

`{"id":"123","type":"PushEvent","payload":{"..."}}`

## Behavior

- The GitHub events endpoint returns only recent activity, not a full history
- The script fetches up to ~300 events per run
- Duplicate events across runs are expected and accepted in Bronze
- Downstream layers are responsible for deduplication and normalization

## Configuration

This script requires a GitHub Personal Access Token via environment variable:

`GITHUB_TOKEN=your_token_here`

Required permission: public repository read access.

## Local execution

Run:

`python main.py`

The script logs pagination progress, the total event count, and the output file path.

## Checkpointing

This service uses a simple S3-backed checkpoint to reduce reprocessing of recently seen events between runs. The checkpoint is intentionally lightweight and is not a deduplication store — Bronze remains append-only.

- Storage: S3 bucket `event-driven-lakehouse-bronz`
- Object key: `checkpoints/repo=apache_spark.json` (per-repo file; template: `checkpoints/repo={owner}_{repo}.json`)
- Format: JSON with a single field:

	`{"last_run_at": "<UTC ISO timestamp>"}`

Behavior summary:

- On start: the pipeline attempts to load the checkpoint from S3. If missing, `last_run_at` defaults to `1970-01-01T00:00:00Z`.
- During ingestion: fetched events are filtered in-memory to keep only those with `created_at` newer than `last_run_at` (a 2-minute margin is applied to the cutoff to reduce edge-case reprocessing).
- After a successful upload of the filtered batch, the checkpoint is overwritten in S3 with the maximum `created_at` from the ingested events using `boto3.put_object`.
- The pipeline emits `checkpoint_loaded` and `checkpoint_updated` structured log events to indicate checkpoint activity.

## Logging

Logs are emitted as single-line JSON objects to stdout to make them readable and queryable in CloudWatch Logs.

- Each log line includes at minimum: `timestamp` (UTC ISO), `event` (semantic name), `repo`, and additional metadata fields.
- Example log line:

	`{"timestamp":"2026-05-31T12:34:56+00:00","event":"s3_upload_complete","repo":"apache/spark","bucket":"...","key":"...","records":42}`

- In CloudWatch Logs / Logs Insights you can parse and query these JSON fields directly for structured searches and metrics.
- The `log_event` helper in the code centralizes the JSON structure and ensures consistent fields across events.

## Future improvements

- Upload JSONL batches directly to S3 Bronze
- Add retry and backoff for API calls
- Add incremental checkpointing
- Add structured logging
- Support ingesting multiple repositories
- Package as Docker / AWS Lambda compatible code

## Integration

This module is the Bronze ingestion component in the lakehouse flow:

GitHub API → Bronze ingestion → S3 Bronze → Lambda / Silver → Athena / dbt → Gold
