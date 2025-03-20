import os
import random
import base64
from io import BytesIO
from PIL import Image

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

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

# TODO: separate this and store the face_dict data in a database
# Load images and convert to feature vectors
face_dict = {}  # Dictionary to store images for each person
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

# Generate verification pairs to be used as test cases
positive_pairs = []
negative_pairs = []
persons = list(face_dict.keys())
persons = [p for p in persons if face_dict[p]] # To ensure only persons with feature vectors are present

# Create positive pairs (same person)
for person, f_vectors in face_dict.items():
    if len(f_vectors) > 1:
        f_vect_1, f_vect_2 = random.sample(f_vectors, 2)
        while np.array_equal(f_vect_1, f_vect_2): # To avoid identical pairs
            f_vect_1, f_vect_2 = random.sample(f_vectors, 2)
        positive_pairs.append((f_vect_1, f_vect_2, True, person, person)) # Set classifier as true

# Create negative pairs (different persons)
num_of_neg_pairs = int(len(persons)/4) 
for _ in range(num_of_neg_pairs): 
    p1, p2 = random.sample(persons, 2)
    f_vect_1 = random.choice(face_dict[p1])
    f_vect_2 = random.choice(face_dict[p2])

    while np.array_equal(f_vect_1, f_vect_2): # To avoid identical pairs
        p1, p2 = random.sample(persons, 2) # Pick new persons
        f_vect_1 = random.choice(face_dict[p1])
        f_vect_2 = random.choice(face_dict[p2])
    
    negative_pairs.append((f_vect_1, f_vect_2, False, p1, p2)) # Set classifier as false

# Combine and shuffle
all_pairs = positive_pairs + negative_pairs
random.shuffle(all_pairs)

y_true = [pair[2] for pair in all_pairs] # Create list consisting of the correct classifiers
y_pred = []

# Test the verification functionality on each test case pair 
for f_vect_1, f_vect_2, has_same_face, p1, p2 in all_pairs:
    prediction = compare_faces_euclidean(f_vect_1, f_vect_2) #prediction, distance = compare_faces_euclidean(f_vect_1, f_vect_2)
    y_pred.append(prediction)
    """ if prediction == has_same_face:
        pass
    else:
        print('Incorrect prediction: ', p1, ' and ', p2)
        print('Distance: ', str(distance)) """

accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)

print(f"Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1-score: {f1:.4f}")

# Confusion matrix
cm = confusion_matrix(y_true, y_pred)

# Ploting
plt.figure(figsize=(5, 4))
plt.imshow(cm, cmap="Blues", interpolation="nearest")
plt.colorbar()

# Labels
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title("Confusion Matrix")

plt.show()
