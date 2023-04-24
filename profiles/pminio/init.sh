#!/bin/bash

set -e

echo "Installing S3 backend"
pip3 install --prefix /usr/local/ --no-cache-dir django-storages[boto3]

echo "Installing Minio client"
curl https://dl.min.io/client/mc/release/linux-amd64/mc \
  --create-dirs \
  -o $HOME/minio-binaries/mc

chmod +x $HOME/minio-binaries/mc
export PATH=$PATH:$HOME/minio-binaries/

echo "export PATH=$PATH:$HOME/minio-binaries/" >> /etc/profile.d/minioclient.sh

echo "Setting up Minio backend"
mc config host add s3 ${PULP_AWS_S3_ENDPOINT_URL} ${PULP_AWS_ACCESS_KEY_ID} ${PULP_AWS_SECRET_ACCESS_KEY} --api S3v4
mc config host rm local

if $(mc find s3/${PULP_AWS_STORAGE_BUCKET_NAME}) ; then
  echo "Minio ${PULP_AWS_STORAGE_BUCKET_NAME} bucket already created"
else
  echo "Creating Minio bucket ${PULP_AWS_STORAGE_BUCKET_NAME}"
  mc mb s3/${PULP_AWS_STORAGE_BUCKET_NAME}
fi
