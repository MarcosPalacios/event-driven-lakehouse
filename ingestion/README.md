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
