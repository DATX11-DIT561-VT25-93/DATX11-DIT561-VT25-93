import onnxruntime as ort
import os
import cv2
import numpy as np

def load_antispoof_model():
    model_path = os.path.join(os.path.dirname(__file__), "AntiSpoofing_print-replay_1.5_128.onnx")
    session = ort.InferenceSession(model_path)
    input_name = session.get_inputs()[0].name
    return session, input_name

def is_real_face(face_crop, session, input_name):
    face_resized = cv2.resize(face_crop, (128, 128)) 
    input_blob = face_resized.astype(np.float32) / 255.0
    input_blob = np.transpose(input_blob, (2, 0, 1))  
    input_blob = np.expand_dims(input_blob, axis=0)  

    result = session.run(None, {input_name: input_blob})[0]
    prob = softmax(result[0])[0]
    print(prob)
    return prob > 0.98

def softmax(logits, decimals=3):
    e = np.exp(logits - np.max(logits))
    probs = e / np.sum(e)
    return np.round(probs, decimals)