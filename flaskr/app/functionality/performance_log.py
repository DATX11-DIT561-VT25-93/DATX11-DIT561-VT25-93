import os
import cv2
import time
import numpy as np
from feature_extraction import extract_feature, init_facenet
from verification import compare_faces_euclidean

DATASET_PATH = 'LFW_dataset' # The path to the dataset folder
TUNED_WEIGHTS_PATH = "facenet_finetuned_weights.h5"
USE_FINE_TUNED = True # Whether to use the fine-tuned weights or not
                   # True  -> Use fine-tuned weights
                   # False -> Use the original weights
REF_INDEX = 0 # The index of the reference image in the dataset

def detect_face_no_base64(image_array):
    model_path = os.path.join(os.path.dirname(__file__), "face_detection_yunet_2023mar.onnx")

    detector = cv2.FaceDetectorYN.create(
        model_path,
        "",
        (320, 320),
        0.9,
        0.1,
        10
    )

    h, w = image_array.shape[:2]
    detector.setInputSize((w, h))

    faces = detector.detect(image_array)[1]
    image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

    if faces is not None:
        return faces, None, image_rgb
    return None, None, None

def evaluate_georgia_tech_faces(model):
    base_dir = os.path.dirname(__file__)
    dataset_path = os.path.join(base_dir, DATASET_PATH) #"gt_db")
    references = {}
    TP = 0
    FP = 0
    FN = 0
    TN = 0
    total_time = 0
    count = 0
    undetected_faces = 0
    misaligned_faces = 0

    for person in sorted(os.listdir(dataset_path)):
        person_path = os.path.join(dataset_path, person)

        images = sorted(f for f in os.listdir(person_path) if f.endswith((".jpg", ".png")))
        ref_img = cv2.imread(os.path.join(person_path, images[REF_INDEX]))

        faces, _, rgb = detect_face_no_base64(ref_img)
        if faces is None:
            undetected_faces += 1
            continue

        emb = extract_feature(faces, rgb, model, True)
        if emb is None: 
            misaligned_faces += 1
            continue

        references[person] = emb

        for img_name in images[1:]:
            img = cv2.imread(os.path.join(person_path, img_name))
            start = time.time()

            faces, _, rgb = detect_face_no_base64(img)
            if faces is None:
                undetected_faces += 1
                continue

            emb = extract_feature(faces, rgb, model) 
            if emb is None: 
                misaligned_faces += 1
                continue

            total_time += time.time() - start
            count += 1

            matched = None
            for ref_label, ref_emb in references.items():
                if compare_faces_euclidean(emb, ref_emb):
                    matched = ref_label
                    break

            if matched == person:
                TP += 1
            elif matched is None:
                FN += 1
            else:
                FP += 1 

    return {
        "True Positives": TP,
        "False Positives": FP,
        "False Negatives": FN,
        "True Negatives": TN,  # Kommer bara vara 0
        "Undetected faces": undetected_faces,
        "Misaligned faces": misaligned_faces,
        "Avg Time/Image (s)": total_time / count if count else 0,
        "Total Classified": count
    }

recognition_model = init_facenet()

if USE_FINE_TUNED:
    #base_dir = os.path.abspath(os.path.dirname(__file__))
    #recognition_model.load_weights(os.path.join(base_dir, "facenet_finetuned_weights.h5"))
    recognition_model.load_weights(TUNED_WEIGHTS_PATH)

results = evaluate_georgia_tech_faces(recognition_model)
for k, v in results.items():
    print(f"{k}: {v}")