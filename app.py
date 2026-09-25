import os
import base64
import time

import cv2
import numpy as np
import serial
from flask import Flask, render_template, request, jsonify
from deepface import DeepFace


# =========================
# CONFIGURATION
# =========================

app = Flask(__name__)

FACES_DIR = "faces"

# Change this to your Arduino COM port
ARDUINO_PORT = "COM3"
ARDUINO_BAUD = 9600

# DeepFace model
MODEL_NAME = "Facenet512"

# Detector options:
# opencv, retinaface, mtcnn, ssd, dlib, mediapipe, yolov8, etc.
DETECTOR_BACKEND = "opencv"

# Distance threshold.
# This is intentionally configurable because the correct value
# depends on the model and your images/environment.
FACE_THRESHOLD = 0.40

# How long the relay remains ON after a successful match
RELAY_ON_TIME = 5


# =========================
# CREATE FOLDERS
# =========================

os.makedirs(FACES_DIR, exist_ok=True)


# =========================
# ARDUINO
# =========================

arduino = None

try:
    arduino = serial.Serial(
        ARDUINO_PORT,
        ARDUINO_BAUD,
        timeout=1
    )

    time.sleep(2)

    print(f"[OK] Arduino connected on {ARDUINO_PORT}")

except Exception as e:
    print("[WARNING] Arduino not connected.")
    print("Reason:", e)


def relay_on():
    """Turn relay ON."""

    if arduino and arduino.is_open:
        try:
            arduino.write(b"ON\n")
            print("[RELAY] ON")
        except Exception as e:
            print("[RELAY ERROR]", e)
    else:
        print("[RELAY] Arduino not connected")


def relay_off():
    """Turn relay OFF."""

    if arduino and arduino.is_open:
        try:
            arduino.write(b"OFF\n")
            print("[RELAY] OFF")
        except Exception as e:
            print("[RELAY ERROR]", e)
    else:
        print("[RELAY] Arduino not connected")


# Always start with relay OFF
relay_off()


# =========================
# LOAD OWNER LIST
# =========================

def get_owners():

    owners = []

    if not os.path.exists(FACES_DIR):
        return owners

    for name in os.listdir(FACES_DIR):

        folder = os.path.join(FACES_DIR, name)

        if os.path.isdir(folder):
            owners.append(name)

    return owners


# =========================
# SAVE BASE64 IMAGE
# =========================

def save_base64_image(image_data, filename):

    try:

        # Remove:
        # data:image/jpeg;base64,
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)

        with open(filename, "wb") as f:
            f.write(image_bytes)

        return True

    except Exception as e:

        print("[IMAGE SAVE ERROR]", e)

        return False


# =========================
# VERIFY FACE
# =========================

def verify_against_owner(image_path, owner_name):

    owner_folder = os.path.join(FACES_DIR, owner_name)

    if not os.path.exists(owner_folder):
        return False, None

    for filename in os.listdir(owner_folder):

        reference_path = os.path.join(
            owner_folder,
            filename
        )

        if not os.path.isfile(reference_path):
            continue

        try:

            result = DeepFace.verify(
                img1_path=reference_path,
                img2_path=image_path,
                model_name=MODEL_NAME,
                detector_backend=DETECTOR_BACKEND,
                distance_metric="cosine",
                enforce_detection=True
            )

            distance = result.get("distance")

            verified = result.get("verified", False)

            print(
                f"[CHECK] {owner_name} | "
                f"distance={distance} | "
                f"verified={verified}"
            )

            if verified and distance is not None:

                if distance <= FACE_THRESHOLD:
                    return True, float(distance)

        except Exception as e:

            print(
                f"[VERIFY ERROR] "
                f"{owner_name}/{filename}: {e}"
            )

    return False, None


# =========================
# HOME PAGE
# =========================

@app.route("/")
def index():
    return render_template(
        "index.html",
        owners=get_owners()
    )


# =========================
# REGISTER PAGE
# =========================

@app.route("/register")
def register():
    return render_template("register.html")


# =========================
# REGISTER FACE
# =========================

@app.route("/register_face", methods=["POST"])
def register_face():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received."
            }), 400

        name = data.get("name", "").strip()
        image_data = data.get("image", "")

        if not name:
            return jsonify({
                "success": False,
                "message": "Please enter owner name."
            }), 400

        if not image_data:
            return jsonify({
                "success": False,
                "message": "No face image received."
            }), 400

        # Prevent unsafe folder names
        safe_name = "".join(
            c for c in name
            if c.isalnum() or c in (" ", "_", "-")
        ).strip()

        if not safe_name:
            return jsonify({
                "success": False,
                "message": "Invalid owner name."
            }), 400

        owner_folder = os.path.join(
            FACES_DIR,
            safe_name
        )

        os.makedirs(owner_folder, exist_ok=True)

        filename = os.path.join(
            owner_folder,
            "face.jpg"
        )

        # Save image
        if not save_base64_image(
            image_data,
            filename
        ):
            return jsonify({
                "success": False,
                "message": "Could not save image."
            }), 500

        # Check that DeepFace can detect a face
        try:

            DeepFace.extract_faces(
                img_path=filename,
                detector_backend=DETECTOR_BACKEND,
                enforce_detection=True
            )

        except Exception as e:

            # Remove invalid image
            if os.path.exists(filename):
                os.remove(filename)

            return jsonify({
                "success": False,
                "message": "No clear face detected. Please try again."
            }), 400

        print(
            f"[REGISTERED] {safe_name}"
        )

        return jsonify({
            "success": True,
            "message": f"{safe_name} registered successfully.",
            "owner": safe_name
        })

    except Exception as e:

        print("[REGISTER ERROR]", e)

        return jsonify({
            "success": False,
            "message": "Registration failed."
        }), 500


# =========================
# SCAN FACE
# =========================

@app.route("/scan", methods=["POST"])
def scan():

    temporary_file = "temp_scan.jpg"

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "match": False,
                "message": "No image received."
            }), 400

        image_data = data.get("image", "")

        if not image_data:
            return jsonify({
                "success": False,
                "match": False,
                "message": "No camera image received."
            }), 400

        # Save camera frame
        if not save_base64_image(
            image_data,
            temporary_file
        ):
            return jsonify({
                "success": False,
                "match": False,
                "message": "Could not process image."
            }), 400

        owners = get_owners()

        if not owners:

            relay_off()

            return jsonify({
                "success": True,
                "match": False,
                "owner": None,
                "message": "No registered owners."
            })

        # Check every registered owner
        for owner in owners:

            matched, distance = verify_against_owner(
                temporary_file,
                owner
            )

            if matched:

                print(
                    f"[ACCESS GRANTED] {owner}"
                )

                relay_on()

                return jsonify({
                    "success": True,
                    "match": True,
                    "owner": owner,
                    "distance": distance,
                    "message": f"Access granted: {owner}"
                })

        # Nobody matched
        print("[ACCESS DENIED]")

        relay_off()

        return jsonify({
            "success": True,
            "match": False,
            "owner": None,
            "message": "Access denied."
        })

    except Exception as e:

        print("[SCAN ERROR]", e)

        # Fail-safe: relay OFF
        relay_off()

        return jsonify({
            "success": False,
            "match": False,
            "message": "Face scan failed."
        }), 500

    finally:

        # Delete temporary scan
        if os.path.exists(temporary_file):

            try:
                os.remove(temporary_file)

            except Exception:
                pass


# =========================
# OWNER LIST
# =========================

@app.route("/owners")
def owners():

    return jsonify({
        "owners": get_owners()
    })


# =========================
# MANUAL RELAY OFF
# =========================

@app.route("/relay_off", methods=["POST"])
def manual_relay_off():

    relay_off()

    return jsonify({
        "success": True,
        "message": "Relay turned OFF."
    })


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":

    print("")
    print("===================================")
    print("       FACE ACCESS SYSTEM")
    print("===================================")
    print("")
    print("Registered owners:")

    for owner in get_owners():
        print(" -", owner)

    print("")
    print("Open:")
    print("http://127.0.0.1:5000")
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )