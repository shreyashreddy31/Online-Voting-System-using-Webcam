from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import pickle
import os
import csv
import base64
from datetime import datetime
from sklearn.neighbors import KNeighborsClassifier

app = Flask(__name__)

# --- CONFIGURATION ---
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

FACES_FILE = os.path.join(DATA_DIR, 'faces_data.pkl')
NAMES_FILE = os.path.join(DATA_DIR, 'names.pkl')
VOTES_FILE = 'Votes.csv'

def train_model():
    if os.path.exists(FACES_FILE) and os.path.exists(NAMES_FILE):
        with open(FACES_FILE, 'rb') as f:
            faces = pickle.load(f)
        with open(NAMES_FILE, 'rb') as f:
            labels = pickle.load(f)
        if len(faces) == len(labels) and len(faces) > 0:
            knn = KNeighborsClassifier(n_neighbors=5)
            knn.fit(faces, labels)
            return knn
    return None

knn = train_model()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/<page>')
def html_page(page): return render_template(page)

@app.route('/api/register', methods=['POST'])
def register_face():
    data = request.json
    aadhaar = data.get('aadhaar')
    image_data = data.get('image')

    try:
        header, encoded = image_data.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except:
        return jsonify({'status': 'error', 'message': 'Image decode failed'}), 400

    facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return jsonify({'status': 'retry'})

    x, y, w, h = faces[0]
    crop_img = gray[y:y+h, x:x+w]
    resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)

    # Save Data
    current_names = []
    if os.path.exists(NAMES_FILE):
        with open(NAMES_FILE, 'rb') as f: current_names = pickle.load(f)
    current_names.append(aadhaar)
    with open(NAMES_FILE, 'wb') as f: pickle.dump(current_names, f)

    if os.path.exists(FACES_FILE):
        with open(FACES_FILE, 'rb') as f: current_faces = pickle.load(f)
        current_faces = np.append(current_faces, resized_img, axis=0)
    else:
        current_faces = resized_img
    with open(FACES_FILE, 'wb') as f: pickle.dump(current_faces, f)

    global knn
    knn = train_model()

    return jsonify({'status': 'success'})

@app.route('/api/predict', methods=['POST'])
def predict_face():
    global knn
    if knn is None: return jsonify({'status': 'error', 'message': 'System initializing...'})

    data = request.json
    image_data = data.get('image')
    
    header, encoded = image_data.split(",", 1)
    nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) == 0: return jsonify({'status': 'retry'})

    x, y, w, h = faces[0]
    crop_img = gray[y:y+h, x:x+w]
    resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
    
    prediction = knn.predict(resized_img)
    predicted_aadhaar = str(prediction[0])

    has_voted = False
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] == predicted_aadhaar:
                    has_voted = True
                    break

    return jsonify({'status': 'success', 'aadhaar': predicted_aadhaar, 'has_voted': has_voted})

@app.route('/api/vote', methods=['POST'])
def cast_vote():
    data = request.json
    aadhaar = data.get('aadhaar')
    party = data.get('party')
    
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] == aadhaar:
                    return jsonify({'status': 'error', 'message': 'Already voted!'})

    ts = datetime.now()
    
    # --- BUG FIX: CHECK EXISTENCE BEFORE OPENING ---
    file_exists = os.path.isfile(VOTES_FILE)
    
    with open(VOTES_FILE, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['NAME', 'VOTE', 'DATE', 'TIME'])
        
        writer.writerow([aadhaar, party, ts.strftime("%d-%m-%Y"), ts.strftime("%H:%M-%S")])
    # -----------------------------------------------
    
    return jsonify({'status': 'success'})

@app.route('/api/results', methods=['GET'])
def get_results():
    results = {'BJP': 0, 'Congress': 0, 'AAP': 0, 'CPIM': 0, 'TMC': 0, 'Others': 0}
    
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'r') as f:
            # Handle potential empty file or bad header
            try:
                reader = csv.DictReader(f)
                for row in reader:
                    party = row.get('VOTE')
                    if party in results:
                        results[party] += 1
                    elif party:
                        results['Others'] += 1
            except:
                pass
                
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)