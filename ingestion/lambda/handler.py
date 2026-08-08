import json
import logging
import os
import sys

from ingestion.main import run_ingestion

logger = logging.getLogger("lambda_ingestion")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.handlers = [handler]


def get_env(name: str, default: str = None, required: bool = False) -> str:
    val = os.getenv(name, default)
    if required and not val:
        raise ValueError(f"Environment variable {name} is required")
    return val


def lambda_handler(event, context):
    token = get_env('GITHUB_TOKEN', required=True)
    bucket = get_env('BRONZE_BUCKET', 'event-driven-lakehouse-bronze')
    checkpoint_bucket = get_env('CHECKPOINT_BUCKET', bucket)
    owner = get_env('GITHUB_OWNER', 'apache')
    repo = get_env('GITHUB_REPO', 'spark')

    result = run_ingestion(owner, repo, token, bucket, checkpoint_bucket)

    return {
        'statusCode': 200,
        'body': json.dumps(result),
    }
