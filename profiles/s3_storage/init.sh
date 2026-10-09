#!/bin/bash

set -e

if ! python3 -c 'import boto3, storages' >/dev/null 2>&1; then
    echo "Installing S3 backend"
    pip3 install --prefix /usr/local/ --no-cache-dir 'django-storages[boto3]'
fi

echo "Setting up RustFS backend"
python3 - <<'PY'
import os
import time

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

endpoint_url = os.environ["PULP_STORAGES__default__OPTIONS__endpoint_url"]
access_key = os.environ["PULP_STORAGES__default__OPTIONS__access_key"]
secret_key = os.environ["PULP_STORAGES__default__OPTIONS__secret_key"]
bucket_name = os.environ["PULP_STORAGES__default__OPTIONS__bucket_name"]

s3 = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name="us-east-1",
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
)

for attempt in range(1, 7):
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"Created RustFS {bucket_name} bucket")
        break
    except Exception as error:
        already_exists = (
            isinstance(error, ClientError)
            and error.response.get("Error", {}).get("Code")
            in {
                "BucketAlreadyOwnedByYou",
                "BucketAlreadyExists",
            }
        )
        if already_exists:
            print(f"RustFS {bucket_name} bucket already created")
            break
        if attempt == 6:
            raise
        print(f"RustFS bucket creation attempt {attempt}/6 failed; retrying in 5 seconds")
        time.sleep(5)
else:
    raise RuntimeError("Failed to create RustFS bucket")
PY
