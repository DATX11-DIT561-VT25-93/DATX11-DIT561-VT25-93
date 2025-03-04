import cv2
import numpy as np


def normalize_vector(vector):
    return vector / np.linalg.norm(vector) # L2 Normalizes a feature vector

def preprocess_face(face):
    face_resized = cv2.resize(face, (160, 160))  # Resize to FaceNet input size
    face_resized = face_resized.astype("float32") / 255.0  # Normalize pixel values
    face_resized = np.expand_dims(face_resized, axis=0)  # Add batch dimension
    return face_resized

def extract_features(faces, image_rgb, model):
    feature_vectors = []

    if faces is not None:
        for face in faces:
            x, y, w, h = map(int, face[:4])
            face_crop = image_rgb[y:y+h, x:x+w]

            if face_crop.shape[0] > 0 and face_crop.shape[1] > 0:
                face_preprocessed = preprocess_face(face_crop)
                feature_vector = model.predict(face_preprocessed)[0]
                feature_vector = normalize_vector(feature_vector)

                feature_vectors.append(feature_vector)
            else:
                feature_vectors.append(np.array([]))

        return feature_vectors

