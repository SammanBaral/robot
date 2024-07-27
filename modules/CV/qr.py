import os
import sys
# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(current_dir)
print(parent_dir)
# Add the parent directory to sys.path
sys.path.append(parent_dir)

from Kinematics.robo import signal_transfer
import cv2
import subprocess

# QR code detection function
# def detect_qr_and_execute(image):
#     detector = cv2.QRCodeDetector()
#     data, bbox, _ = detector.detectAndDecode(image)
#     if data: 
#         print(f"QR Code detected: {data}")
#         # Stop the robot by sending stop command
#         signal_transfer.send_wheel_command(arduino,0, 0)
#         arduino.close()  # Close serial connection
#         # Run your script
#         #TODO:
#         function_call = 'from modules.NLP.TSS import speak; speak("Hello")'
#         subprocess.call(["python", "-c", function_call])

#         return True
#     return False

import qrcode
from cryptography.fernet import Fernet

def generate_qr(new_command):
    # Generate a key for encryption
    key = Fernet.generate_key()
    cipher = Fernet(key)
    data=new_command
    # The command you want to encrypt
    

    # Encrypt the command
    encrypted_command = cipher.encrypt(data.encode())

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(encrypted_command)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save("new_QR.png")

    # Save the encryption key for later decryption (keep this secure)
    with open("encryption_key.key", "wb") as key_file:
        key_file.write(key)


def detect_qr_code(image, key_file="encryption_key.key"):
    def decrypt_data(data):
        """Decrypt data using the given cipher."""
        cipher=Fernet(key)
        return cipher.decrypt(data.encode()).decode()
    
    # Load the encryption key from the file
    with open(key_file, 'rb') as f:
        key = f.read()

    # Initialize QR code detector
    detector = cv2.QRCodeDetector()
    
    # Detect and decode QR code
    data, bbox, _ = detector.detectAndDecode(image)
    if data:
        # Decrypt the data using the encryption key
        decrypted_data = decrypt_data(data)
        return decrypted_data   
        
        
    else:
        return None
    

# generate_qr("This is the first ring King Tribhuvan gifted to then Crown Prince Mahendra. He then gave it to King Birendra before his coronation.")
