import cv2
import numpy as np
from deepface.models.facial_recognition import Facenet
import os

def init_facenet():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    new_deepface_home = os.path.join(base_dir, "facenet_weights")
    os.makedirs(new_deepface_home, exist_ok=True)
    os.environ["DEEPFACE_HOME"] = new_deepface_home

    rec_model = Facenet.load_facenet512d_model()
    warmup_input = np.random.rand(1, 160, 160, 3)
    rec_model.predict(warmup_input)
    return rec_model

def normalize_vector(vector):
    return vector / np.linalg.norm(vector) # L2 Normalizes a feature vector

def preprocess_face(face):
    face_resized = cv2.resize(face, (160, 160))  # Resize to FaceNet input size
    face_resized = face_resized.astype("float32") / 255.0  # Normalize pixel values
    face_resized = np.expand_dims(face_resized, axis=0)  # Add batch dimension
    return face_resized

def bounding_box_area(face):
    x, y, w, h = map(int, face[:4])
    return w * h

def extract_feature(faces, image_rgb, model):
    closest_face = max(faces, key=bounding_box_area)
    
    x, y, w, h = map(int, closest_face[:4])
    face_crop = image_rgb[y:y+h, x:x+w]

    face_preprocessed = preprocess_face(face_crop)
    feature_vector = model.predict(face_preprocessed)[0]
    feature_vector = normalize_vector(feature_vector)

    return feature_vector

