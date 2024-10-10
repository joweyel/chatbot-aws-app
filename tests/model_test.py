import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import numpy as np
import pytest
from streamlit_app import (
    load_detection_model,
    load_landmarks_model,
    detect_faces
)

## Testing the loading of different model types
def test_load_detection_model_caffe():
    """Test loading of caffe model"""
    net = load_detection_model(net_type="caffe")
    assert net is not None, "Error when loading Caffe model"

def test_load_detection_model_tf():
    """Test loading of TensorFlow model"""
    net = load_detection_model(net_type="tf")
    assert net is not None, "Error when loading TensorFlow model"

def test_load_detection_model_invalid():
    """Test loading of of detected model with invalid input"""
    with pytest.raises(ValueError):
        _ = load_detection_model(net_type="xyz")

def test_load_landmarks_model():
    """Test loading of facial landmarks model"""
    net = load_landmarks_model()
    assert net is not None, "Error when loading landmarks model"

def test_detect_faces_no_face():
    """Testing the face detection in the case of no faces"""
    net = load_detection_model(net_type="caffe")
    img_black = np.zeros((300, 300, 3), dtype=np.uint8)
    thresholds = np.arange(0.5, 1.0, 0.1)
    for t in thresholds:
        detections = detect_faces(net, img_black, threshold=t)
        assert len(detections) == 0, "There should be no face in a black image"

def test_detect_faces_one_face():
    """Testing the face detection in the case of one face"""
    net = load_detection_model(net_type="caffe")
    img_face = cv2.imread("images/dl_dude.jpg")  # pylint: disable=E1101:no-member

    thresholds = np.arange(0.5, 1.0, 0.1)
    for t in thresholds:
        detections = detect_faces(net, img_face, threshold=t)
        assert len(detections) == 1, "There should be one face in the image"
