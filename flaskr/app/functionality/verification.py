import numpy as np


def compare_faces_euclidean(vec1, vec2, threshold=0.8):
    distance = np.linalg.norm(vec1 - vec2)
    #print(distance)
    if distance < threshold:
        return True
    return False

def compare_faces_cosine(vec1, vec2):
    cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    print(cosine_similarity)
