from flask import Blueprint, render_template, jsonify, request, current_app

face_auth_bp = Blueprint('face_auth_bp', __name__)



@face_auth_bp.route('/frame', methods=['POST'])
def handle_frame():
    
    data = request.get_json()
    
    if 'image' not in data:
        return jsonify({'error': 'No image received'}), 400

    try:
        # Extract and decode the image
        image_data = data['image'].split(',')[1]  # Remove 'data:image/jpeg;base64,'

        # Perform face detection
        """ image_bytes = base64.b64decode(image_data)

        # Convert to PIL Image (optional for processing)
        image = Image.open(io.BytesIO(image_bytes))

        # Convert the image to OpenCV format (if needed)
        open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # You can perform face detection here
        face_image = detect_face(open_cv_image)
        
        if face_image is not None:
            #face_pil = Image.fromarray(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))
            #face_pil.show()  # Opens the image in the default viewer
            return jsonify({'message': 'Face detected'})

        #image.show()  # Open the image for debugging """

    except Exception as e:
        return jsonify({"error": f"Invalid image data: {str(e)}"}), 400

    return jsonify({'message': 'No face detected'})