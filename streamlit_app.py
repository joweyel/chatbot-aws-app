import numpy as np
import cv2
import streamlit as st

MAX_DETECTIONS = 10
NET_TYPE = "caffe"

@st.cache_resource()
def load_detection_model(net_type="caffe"):
    if net_type == "caffe":
        model_file = "./models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
        config_file = "./models/deploy.prototxt"
        net = cv2.dnn.readNetFromCaffe(config_file, model_file)
    elif net_type == "tf":
        model_file = "./models/opencv_face_detector_uint8.pb"
        config_file = "./models/opencv_face_detector.pbtxt"
        net = cv2.dnn.readNetFromTensorflow(model_file, config_file)
    else:
        raise ValueError(f"Unsupported network type: {net_type}")

    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    print("Face detection model loaded")
    return net

@st.cache_resource()
def load_landmarks_model():
    net = cv2.face.createFacemarkLBF()
    model_file = "./models/lbfmodel.yaml"
    net.loadModel(model_file)
    print("Facial landmark detection model loaded")
    return net

def detect_faces(net, img, threshold):

    # Part 1: get face detections
    blob = cv2.dnn.blobFromImage(
        img,
        scalefactor=1.0,
        size=(300, 300),
        mean=(104.0, 117.0, 123.0),
        swapRB=False,
        crop=False
    )

    net.setInput(blob)
    detections = net.forward()

    def bounds_check(p1, p2, h, w):
        h_check = 0 <= p1[1] < h and 0 <= p2[1] <= h
        w_check = 0 <= p1[0] < w and 0 <= p2[0] <= w
        return w_check and h_check

    def validity_check(det_h, det_w):
        return det_h > 0 and det_w > 0

    # Part 2: get the bboxes of all detectons
    faces = []
    H, W = img.shape[0], img.shape[1]
    for det in detections[0][0]:
        if det[2] >= threshold:
            p1 = [det[3] * W, det[4] * H]  # [x1, y1]
            p2 = [det[5] * W, det[6] * H]  # [x2, y2]
            det_w = p2[0] - p1[0]
            det_h = p2[1] - p1[1]
            if bounds_check(p1, p2, H, W) and \
                validity_check(det_h, det_w):
                faces.append((p1[0], p1[1], det_w, det_h))

    return np.array(faces).astype(int)

st.title("Facial landmark detection")

img_file_buffer = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

net_facedet = load_detection_model(NET_TYPE)
net_lmarks = load_landmarks_model()


if img_file_buffer is not None:
    img_bytes = np.asarray(bytearray(img_file_buffer.read()), dtype=np.uint8)
    img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR) # pylint: disable=E1101:no-member

    placeholder = st.columns(2)
    with placeholder[0]:
        st.image(img, width=300, channels="BGR")
        st.text("Input Image")

    conf_threshold = st.slider(
        "Confidence threshold", 
        min_value=0.0, max_value=1.0,
        step=0.01, value=0.5
    )

    detections = detect_faces(net_facedet, img, conf_threshold)
    st.text(f"Number of detections {len(detections)}")

    img_lmarks = img.copy()
    if len(detections) > 0 and len(detections) < MAX_DETECTIONS:
        retval, landmarksList = net_lmarks.fit(img, detections)

        for lmarks in landmarksList:
            cv2.face.drawFacemarks(img_lmarks, lmarks, (0, 255, 0))

        with placeholder[1]:
            st.image(img_lmarks, width=300, channels="BGR")
            st.text("Detected faces with facial landmarks")
