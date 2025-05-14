import base64
import cv2
import numpy as np
from io import BytesIO
import os
from PIL import Image

def detect_face(base64_string):
    image = process_base64_image(base64_string)
    
    model_path = os.path.join(os.path.dirname(__file__), "face_detection_yunet_2023mar.onnx")

    # Initialize the YuNet face detector
    detector = cv2.FaceDetectorYN.create(
        model_path, #'face_detection_yunet_2023mar.onnx',  # Downloaded from OpenCV model zoo
        "",         # Backend target (usually left empty)
        (320, 320), # Default size for the detector
        0.9,        # Confidence threshold
        0.1,        # Non Max Supression (NMS) threshold
        10         # Max number of detections
    )

    # Convert image and detect faces
    h, w = image.shape[:2]
   
    detector.setInputSize((w, h))

    faces = detector.detect(image)[1] 

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    if faces is not None:
        image_w_rectangles = draw_face_rectangles(image, faces) # Image with marked faces in shape of base64 string 
        return (faces, image_w_rectangles, image_rgb)
    
    return (None, None, None)

# Turns base64 image string into shape that our OpenCV face detector can handle
def process_base64_image(base64_string):
    try:
        image_data = base64_string

        if ',' in base64_string:
            image_data = base64_string.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)

        # Displaying the image
        #image = Image.open(BytesIO(image_bytes))
        #image.show()
        
        image_np_array = np.frombuffer(image_bytes, dtype=np.uint8)
        
        cv_image = cv2.imdecode(image_np_array, cv2.IMREAD_COLOR)
        
        if cv_image is None:
            raise ValueError("Failed to decode the image")

        return cv_image
    except Exception as e:
        print(f"Error processing Base64 image: {str(e)}")
        return None

# Turns OpenCV image into base4 image string that our backend can handle
def to_base64_image(image_rgb):
    _, buffer = cv2.imencode('.jpg', image_rgb)  
    byte_data = buffer.tobytes()  
    base64_string = base64.b64encode(byte_data).decode('utf-8')
    
    return base64_string

def draw_face_rectangles(image, faces):
    for face in faces:
        x, y, w, h = map(int, face[:4]) 
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green box

    base64_string = to_base64_image(image)

    # Displaying the image
    #face_pil = Image.fromarray(image)
    #face_pil.show()  # Opens the image in the default viewer

    return base64_string  # Return image with marked faces in shape of base64 string

##########################
##########################
##########################

# Only used for running performance tests
def detect_face_for_testing(image_array):
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
