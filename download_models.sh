#!/bin/bash

# Define the release URL
RELEASE_URL="https://github.com/joweyel/face-landmark-app/releases/download/model"

# Create the models directory if it doesn't exist
mkdir -p models

# Download the files into the models directory
wget -c -P models "${RELEASE_URL}/deploy.prototxt"
wget -c -P models "${RELEASE_URL}/lbfmodel.yaml"
wget -c -P models "${RELEASE_URL}/opencv_face_detector.pbtxt"
wget -c -P models "${RELEASE_URL}/opencv_face_detector_uint8.pb"
wget -c -P models "${RELEASE_URL}/res10_300x300_ssd_iter_140000_fp16.caffemodel"

echo "Files downloaded successfully into the models directory."