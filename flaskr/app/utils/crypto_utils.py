from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def encrypt_aes_gcm(plaintext: str, key: bytes):

    if len(key) not in [16, 24, 32]:  
        raise ValueError("AES key must be 16, 24, or 32 bytes long")
    
    iv = os.urandom(12)  # AES-GCM requires a 12-byte IV
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()  
    auth_tag = encryptor.tag  
    
    return {
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "iv": base64.b64encode(iv).decode(),
        "auth_tag": base64.b64encode(auth_tag).decode()
    }

def decrypt_aes_gcm(ciphertext: str, key: bytes, iv: str, auth_tag: str):
    cipher = Cipher(algorithms.AES(key), modes.GCM(bytes.fromhex(iv), bytes.fromhex(auth_tag)), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_text = decryptor.update(bytes.fromhex(ciphertext)) + decryptor.finalize()

    return decrypted_text.decode()