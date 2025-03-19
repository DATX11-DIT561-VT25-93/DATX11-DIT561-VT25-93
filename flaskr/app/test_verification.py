import os
import random
import base64
from io import BytesIO
from PIL import Image
import numpy as np

from functionality.detection import detect_face
from functionality.feature_extraction import extract_feature
from functionality.verification import compare_faces_euclidean
from deepface.models.facial_recognition import Facenet
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
new_deepface_home = os.path.join(base_dir, "functionality", "facenet_weights")
os.makedirs(new_deepface_home, exist_ok=True)
os.environ["DEEPFACE_HOME"] = new_deepface_home

rec_model = Facenet.load_facenet512d_model()

# Path to dataset
DATASET_PATH = "test_images"

# Load images and convert to feature vectors
face_dict = {}  # Dictionary to store images per person
for person in os.listdir(DATASET_PATH):
    person_path = os.path.join(DATASET_PATH, person)
    if os.path.isdir(person_path):
        face_dict[person] = []
        for img_name in os.listdir(person_path):
            img_path = os.path.join(person_path, img_name)
            with open(img_path, "rb") as img_file:
                base64_string = base64.b64encode(img_file.read()).decode("utf-8")
                face_data, _, image_rgb = detect_face(base64_string) # Get array containing face data and image with marked faces in shape of base64 string
           
                if face_data is not None:
                    feature_vector = extract_feature(face_data, image_rgb, rec_model)
                    face_dict[person].append(feature_vector)
                else:
                    print("No face detected")

# Generate verification pairs
positive_pairs = []
negative_pairs = []
persons = list(face_dict.keys())

# Create positive pairs (same person)
for person, f_vectors in face_dict.items():
    if len(f_vectors) > 1:
        for _ in range(5):  # Generate multiple pairs per person
            img1, img2 = random.sample(f_vectors, 2)
            positive_pairs.append((img1, img2, True, person, person))

# Create negative pairs (different persons)
for _ in range(5 * len(persons)): 
    p1, p2 = random.sample(persons, 2)
    img1 = random.choice(face_dict[p1])
    img2 = random.choice(face_dict[p2])
    negative_pairs.append((img1, img2, False, p1, p2))

# Combine and shuffle
all_pairs = positive_pairs + negative_pairs
random.shuffle(all_pairs)

for i in range(len(all_pairs)):
    _, _, status, p1, p2 = all_pairs[i]
    print('Pair number ', str(i), ' ', p1, ' and ', p2)
    print(str(status) + '\n')


