from flask import Flask, render_template, Response, redirect, session, send_file , request ,url_for ,jsonify
import numpy as np
import imutils
import pickle
import cv2
import time
from datetime import datetime
import json
import os
import csv
import io


from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.secret_key = "mysecretkey123" 

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0606@localhost:5433/attendance_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --------- Student Table ---------

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    rollno = db.Column(db.Integer)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Present")
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)




# Create tables
with app.app_context():
    db.create_all()

# -------------------------------
# Load Models 
# -------------------------------
embeddingModel = "model/openface_nn4.small2.v1.t7"
recognizerFile = "output/recognizer.pickle"
labelEncFile = "output/le.pickle"
conf = 0.5

print("Loading models...")
prototxt = "model/deploy.prototxt"
model = "model/res10_300x300_ssd_iter_140000.caffemodel"
detector = cv2.dnn.readNetFromCaffe(prototxt, model)
embedder = cv2.dnn.readNetFromTorch(embeddingModel)
recognizer = pickle.loads(open(recognizerFile, "rb").read())
le = pickle.loads(open(labelEncFile, "rb").read())

attendance = {}   # Stores {name: {date, time}}
message = ""      # Temporary success message

ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "Admin"




    
def mark_attendance(name):
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M:%S")

    with app.app_context():   
        existing = Attendance.query.filter_by(student_name=name, date=date_str).first()

        if not existing:
            new_entry = Attendance(
                student_name=name,
                date=date_str,
                time=time_str,
                status="Present"   # ✅ FIX ADDED
            )
            db.session.add(new_entry)
            db.session.commit()
            print(f"✅ Attendance marked for {name}")
        else:
            print(f"⚠️ {name} already marked today")




# ---- Load registered students ----
def load_registered_students():
    students = []
    try:
        with open('student.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    students.append({"name": row[0], "roll": row[1]})
    except FileNotFoundError:
        pass
    return students



# -------------------------------
# Generate Camera Frames
# -------------------------------
def generate_frames():
    global message
    cam = cv2.VideoCapture(0)
    time.sleep(2.0)
    message_display_time = 0

    while True:
        success, frame = cam.read()
        if not success:
            break

        frame = imutils.resize(frame, width=600)
        (h, w) = frame.shape[:2]

        # Detect face
        imageBlob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            1.0, (300, 300),
            (104.0, 177.0, 123.0),
            swapRB=False, crop=False
        )
        detector.setInput(imageBlob)
        detections = detector.forward()

        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                face = frame[startY:endY, startX:endX]
                (fH, fW) = face.shape[:2]
                if fW < 20 or fH < 20:
                    continue

                faceBlob = cv2.dnn.blobFromImage(
                    face, 1.0 / 255, (96, 96), (0, 0, 0),
                    swapRB=True, crop=False
                )
                embedder.setInput(faceBlob)
                vec = embedder.forward()

                preds = recognizer.predict_proba(vec)[0]
                j = np.argmax(preds)
                proba = preds[j]
                name = le.classes_[j]

                if proba >= 0.70:
                    with app.app_context():
                        mark_attendance(name)
                        text = "{} : {:.2f}%".format(name, proba * 100)
                        message_display_time = time.time()
                    
                else:
                    text = "Unknown"

            
                y = startY - 10 if startY - 10 > 10 else startY + 10
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                cv2.putText(frame, text, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # ✅ Show success message for 3 seconds
        if message and time.time() - message_display_time < 3:
            cv2.putText(frame, message, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        elif time.time() - message_display_time >= 3:
            message = ""

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cam.release()

# -------------------------------
# Flask Routes
# -------------------------------



@app.route('/')
def index():
    """Homepage — Live Camera"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')




# @app.route('/attendance')
# def show_attendance():
#     data = Attendance.query.all()
#     return render_template('attendance.html', data=data)

@app.route('/attendance')
def show_attendance():
    data = Attendance.query.order_by(Attendance.id.desc()).all()
    return render_template('attendance.html', data=data)





from datetime import date
from sqlalchemy import func

# @app.route('/absent')
# def show_absent_page():
#     today = date.today()

#     # Get all attendance records for today
#     data = Attendance.query.filter(Attendance.date == today.strftime("%Y-%m-%d")).all()

#     # Extract present student names
#     present_names = {row.student_name for row in data}

#     # Late students (after 09:15 AM)
#     late_students = Attendance.query.filter(
#         Attendance.date == today.strftime("%Y-%m-%d"),
#         Attendance.time > "09:15:00"
#     ).all()

#     # Get all student names from Student table
#     all_students = Student.query.all()
#     all_names = {student.name for student in all_students}

#     # Absent students = all students - present students
#     absentees = sorted(all_names - present_names)

#     return render_template(
#         "absent.html",
#         data=data,
#         late_students=late_students,
#         absentees=absentees,
#         current_date=today.strftime("%Y-%m-%d")
#     )

from sqlalchemy import or_, cast, String
from sqlalchemy import or_  



@app.route('/absent', methods=['GET'])
def show_absent_page():
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    # --- Present / Late students ---
    data = Attendance.query.filter(Attendance.date == today_str).all()
    late_students = Attendance.query.filter(
        Attendance.date == today_str,
        Attendance.time > "09:15:00"
    ).all()

    # --- Absent students ---
    all_students = Student.query.all()
    all_names = {student.name for student in all_students}
    present_names = {row.student_name for row in data}
    absentees = sorted(all_names - present_names)

    # --- Search functionality ---
    search_query = request.args.get('search', '').strip()
    search_results = None

    if search_query:
        # Search Attendance table
        search_results = Attendance.query.filter(
            or_(
                Attendance.student_name.ilike(f"%{search_query}%"),
                Attendance.status.ilike(f"%{search_query}%"),
                cast(Attendance.date, String).ilike(f"%{search_query}%"),
                cast(Attendance.time, String).ilike(f"%{search_query}%")
            )
        ).all()

        # Include matching absent students from absentees
        absentees_filtered = [s for s in absentees if search_query.lower() in s.lower()]
    else:
        absentees_filtered = absentees

    return render_template(
        "absent.html",
        data=data,
        late_students=late_students,
        absentees=absentees_filtered,
        current_date=today_str,
        search_query=search_query,
        search_results=search_results
    )



@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            # Redirect admin to the absent page after login
            return redirect(url_for('show_absent_page'))

        else:
            return render_template('admin_login.html', error="Invalid credentials!")

    return render_template('admin_login.html')



@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('show_attendance'))

@app.route('/add', methods=['POST'])
def add_student():
    data = request.get_json()
    new_student = Student(name=data['name'], rollno=data['rollno'])
    db.session.add(new_student)
    db.session.commit()
    return jsonify({'message': 'Student added successfully'})

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    result = [{'id': s.id, 'name': s.name, 'rollno': s.rollno} for s in students]
    return jsonify(result)

@app.route('/update/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'message': 'Student not found'})
    data = request.get_json()
    student.name = data.get('name', student.name)
    student.rollno = data.get('rollno', student.rollno)
    db.session.commit()
    return jsonify({'message': 'Student updated successfully'})


@app.route('/delete_attendance/<int:id>', methods=['POST'])
def delete_attendance(id):
    record = Attendance.query.get(id)
    if record:
        db.session.delete(record)
        db.session.commit()
    return redirect(url_for('show_attendance'))




if __name__ == "__main__":
    app.run(debug=True)

