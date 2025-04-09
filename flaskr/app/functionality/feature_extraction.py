import cv2
import numpy as np
from deepface.models.facial_recognition import Facenet
import onnxruntime as ort
from anti_spoof import is_real_face
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

def crop_face_with_padding(image, x, y, w, h, padding=30):
    height, width = image.shape[:2]
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(width, x + w + padding)
    y2 = min(height, y + h + padding)
    return image[y1:y2, x1:x2]


def is_face_aligned(face):
    x1, y1 = face[4:6]  # Left eye
    x2, y2 = face[6:8]  # Right eye
    x3, y3 = face[8:10] # Nose
    x4, y4 = face[10:12] # Left mouth corner
    x5, y5 = face[12:14] # Right mouth corner

    eye_distance = abs(x2 - x1)  

    eye_height_diff_ratio = abs(y2 - y1) / eye_distance 
    print("\nEye height diff: ", eye_height_diff_ratio)

    mouth_corner_height_diff_ratio = abs(y5 - y4) / eye_distance
    print("Mouth corner height diff: ", mouth_corner_height_diff_ratio)

    nose_offset_ratio = abs((x1 + x2) / 2 - x3) / eye_distance
    print("Nose offset ratio: ", nose_offset_ratio)

    return eye_height_diff_ratio < 0.12 and mouth_corner_height_diff_ratio < 0.09 and nose_offset_ratio < 0.1

def extract_feature(faces, image_rgb, model, antispoof_sess, input_name):
    closest_face = max(faces, key=bounding_box_area)
    
    if not is_face_aligned(closest_face) or bounding_box_area(closest_face) < 8000:
        print("Face is not positioned properly. Skipping feature extraction.\n")
        return None
    
    print("Bounding box area", bounding_box_area(closest_face))

    print("Face is positioned properly.\n")

    x, y, w, h = map(int, closest_face[:4])
    face_crop = image_rgb[y:y+h, x:x+w]

    if not is_real_face(crop_face_with_padding(image_rgb, x, y, w, h, padding=30), antispoof_sess, input_name):
        print("Spoof detected. Skipping feature extraction.\n")
        return None

    print("Real face confirmed.\n")

    face_preprocessed = preprocess_face(face_crop)
    feature_vector = model.predict(face_preprocessed)[0]
    feature_vector = normalize_vector(feature_vector)

    return feature_vector

###################################
###################################
###################################

# Only used for running anti-spoofing tests
def predict_spoof(face_data, image_rgb, antispoof_sess, antispoof_input):
    closest_face = max(face_data, key=bounding_box_area)
    x, y, w, h = map(int, closest_face[:4])
    padded_face_crop = crop_face_with_padding(image_rgb, x, y, w, h, padding=30)

    return is_real_face(padded_face_crop, antispoof_sess, antispoof_input)
