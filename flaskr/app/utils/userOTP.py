import math
import random
import os
from flask import jsonify, request, current_app
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .crypto_utils import encrypt_aes_gcm, decrypt_aes_gcm  # you already have this
# You also need a Supabase DB client set up here

load_dotenv()

AES_KEY = bytes.fromhex(os.getenv("AESGCM_SECRET_KEY"))

# Generates a 6-digit numeric OTP
def generate_otp(session_id: str, user_email: str):
    with current_app.app_context():
        supabase = current_app.supabase

        digits = "0123456789"
        otp = ''.join(random.choice(digits) for _ in range(6))
        encrypted_data = encrypt_aes_gcm(str(otp), AES_KEY)

        supabase.table("temp_otp").insert({
            "session_id": session_id,
            "encrypted_otp": encrypted_data["ciphertext"],
            "iv": encrypted_data["iv"],
            "auth_tag": encrypted_data["auth_tag"],
            "status": "unused"
        }).execute()

        send_email(user_email, str(otp))

    return True

def verify_otp(session_id: str, typed_otp: str):
    with current_app.app_context():
        supabase = current_app.supabase
        
        response = supabase.table("temp_otp").select("*").eq("session_id", session_id).eq("status", "unused").order("created_at", desc=True).limit(1).execute()
        
        if not response.data:
            return False

        r = response.data[0]
        ciphertext = r["encrypted_otp"]
        iv = r["iv"]
        auth_tag = r["auth_tag"]

        try:
            decrypted_otp = decrypt_aes_gcm(ciphertext, AES_KEY, iv, auth_tag)
            if typed_otp == decrypted_otp:
                # Mark OTP as used
                supabase.table("temp_otp").update({"status": "used"}).eq("session_id", session_id).execute()
                return True
        except Exception as e:
            print(f"Decryption error: {e}")

    return False

def send_email(email_address: str, otp: str):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print("Missing email credentials in environment (.env)")
        return False

    # Compose HTML message
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 500px;
                margin: 40px auto;
                background: #fff;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                padding: 40px;
                text-align: center;
            }}
            .otp-code {{
                font-size: 32px;
                letter-spacing: 10px;
                font-weight: bold;
                color: #2b2b2b;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 40px;
                font-size: 12px;
                color: #888;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Your One-Time Passcode</h2>
            <p>Use the following code to log in. It expires shortly, don't share it with anyone.</p>
            <div class="otp-code">{otp}</div>
            <p>If you didn't request this, please ignore this email.</p>
            <div class="footer">
                &copy; 2025 BioAuth.
            </div>
        </div>
    </body>
    </html>
    """

    try:
        # Create MIME message
        message = MIMEMultipart("alternative")
        message["Subject"] = "BioAuth - Your Login OTP"
        message["From"] = sender_email
        message["To"] = email_address

        # Attach HTML content
        message.attach(MIMEText(html, "html"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email_address, message.as_string())

        print("OTP sent via email.")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False