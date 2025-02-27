from flask import Blueprint, render_template, jsonify, request, current_app, redirect, url_for, session
#import base64
#import io
#from PIL import Image

face_auth_bp = Blueprint('face_auth_bp', __name__)


@face_auth_bp.route('/register-face-detection', methods=['POST', 'GET']) 
def register():
    #supabase = current_app.supabase
    if request.method == 'POST':
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image received'}), 400

        try:
            # Extract and decode the image
            print("Webcam frame received")
            image_data = data['image'].split(',')[1] # Remove 'data:image/jpeg;base64,'

            # Uncomment the three lines below (and import packages above) to see what the webcam frames looks like from the Python point of view
            #image_bytes = base64.b64decode(image_data) 

            # Convert to PIL Image (optional for processing)
            #image = Image.open(io.BytesIO(image_bytes))

            #image.show()  # Open the image for debugging
            
            ######################################
            # TODO: Perform face detection below #
            ######################################
            """ # Convert the image to OpenCV format (if needed)
            open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # You can perform face detection here
            face_image = detect_face(open_cv_image)
            
            if face_image is not None:
                #face_pil = Image.fromarray(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))
                #face_pil.show()  # Opens the image in the default viewer
                return jsonify({'message': 'Face detected'}) """

        except Exception as e:
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400

        return jsonify({'message': 'No face detected'})

    return render_template('register-face-detection.html')



@face_auth_bp.route('/login-face-detection', methods=['POST', 'GET'])
def login():
    #supabase = current_app.supabase

    if request.method == 'POST':
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image received'}), 400

        try:
            # Extract and decode the image
            print("Webcam frame received")
            image_data = data['image'].split(',')[1] # Remove 'data:image/jpeg;base64,'

            # Uncomment the three lines below (and import packages above) to see what the webcam frames looks like from the Python point of view
            #image_bytes = base64.b64decode(image_data) 

            # Convert to PIL Image (optional for processing)
            #image = Image.open(io.BytesIO(image_bytes))

            #image.show()  # Open the image for debugging
            
            ######################################
            # TODO: Perform face detection below #
            ######################################
            """ # Convert the image to OpenCV format (if needed)
            open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # You can perform face detection here
            face_image = detect_face(open_cv_image)
            
            if face_image is not None:
                #face_pil = Image.fromarray(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))
                #face_pil.show()  # Opens the image in the default viewer
                return jsonify({'message': 'Face detected'}) """

        except Exception as e:
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400

        return jsonify({'message': 'No face detected'})

    return render_template('login-face-detection.html')

