
from deepface.models.facial_recognition import Facenet
import cv2
import os

# Functions for activating the face detection and feature extraction model, respectively 

def init_detection_model():
    model_path = os.path.join(os.path.dirname(__file__), "face_detection_yunet_2023mar.onnx")

    detector = cv2.FaceDetectorYN.create(
        model_path,
        "",
        (320, 320),
        0.9,
        0.1,
        10
    )

    return detector

def init_recognition_model():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    new_deepface_home = os.path.join(base_dir, "facenet_weights")
    os.makedirs(new_deepface_home, exist_ok=True)
    os.environ["DEEPFACE_HOME"] = new_deepface_home

    rec_model = Facenet.load_facenet512d_model()
    
    return rec_model
