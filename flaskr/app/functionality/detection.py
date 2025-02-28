import cv2

def detect_face(frame):
    # Initialize the YuNet face detector
    detector = cv2.FaceDetectorYN.create(
        'face_detection_yunet_2023mar.onnx',  # Downloaded from OpenCV model zoo
        "",         # Backend target (usually left empty)
        (320, 320), # Default size for the detector
        0.9,        # Confidence threshold
        0.3,        # Non Max Supression (NMS) threshold
        10          # Max number of detections
    )

    # Convert frame and detect faces
    h, w = frame.shape[:2]
    detector.setInputSize((w, h))
    faces = detector.detect(frame)[1] # Returns an array with length 15 and dtype=float32

    return faces

    #if faces is None:
        #return jsonify({'error':'No face was detected, make sure you are in front of the camera'})
        #detect_faces(next_frame)
    
    #elif len(faces) > 1:
        #return jsonify({'error':'More than one face was detected, make sure only one person is in front of the camera'})
        #detect_faces(next_frame)
        
    #else:
        #return jsonify({'message': 'Face detected'})
