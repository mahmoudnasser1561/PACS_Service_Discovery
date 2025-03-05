#!/bin/bash
# Script to add a new Orthanc server dynamically

if [ -z "$1" ]; then
  echo "Usage: $0 <container_number>"
  exit 1
fi

CONTAINER_NUM=$1
PORT_WEB=$((8042 + CONTAINER_NUM))
PORT_DICOM=$((4242 + CONTAINER_NUM))
CONTAINER_NAME="orthanc${CONTAINER_NUM}"


docker run -d \
  --name $CONTAINER_NAME \
  -p ${PORT_WEB}:8042 \
  -p ${PORT_DICOM}:4242 \
  -e ORTHANC_JSON='{"Name": "'"$CONTAINER_NAME"'", "AuthenticationEnabled": false}' \
  jodogne/orthanc


echo "Orthanc server $CONTAINER_NAME started successfully!"
echo "Web interface: http://localhost:$PORT_WEB/app/explorer.html"
echo "DICOM port: $PORT_DICOM"