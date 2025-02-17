from flask import Blueprint, render_template, jsonify, request, current_app

face_auth_bp = Blueprint('face_auth_bp', __name__)




# For later
@face_auth_bp.route('/frame', methods=['POST'])
def handle_frame():
    #frame = request...
    return 'Frame handled'