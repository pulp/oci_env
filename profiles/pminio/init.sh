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
ENDPOINT_URL="${PULP_STORAGES__default__OPTIONS__endpoint_url}"
ACCESS_KEY="${PULP_STORAGES__default__OPTIONS__access_key}"
SECRET_KEY="${PULP_STORAGES__default__OPTIONS__secret_key}"
BUCKET_NAME="${PULP_STORAGES__default__OPTIONS__bucket_name}"
mc alias set s3 ${ENDPOINT_URL} ${ACCESS_KEY} ${SECRET_KEY} --api S3v4
mc alias rm local
mc admin info s3

if $(mc find s3/${BUCKET_NAME}) ; then
  echo "Minio ${BUCKET_NAME} bucket already created"
else
  echo "Creating Minio bucket ${BUCKET_NAME}"
  mc mb s3/${BUCKET_NAME}
fi
