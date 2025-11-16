# from flask import Flask, render_template, Response, redirect, session, send_file , request ,url_for ,jsonify
# import numpy as np
# import imutils
# import pickle
# import cv2
# import time
# from datetime import datetime
# import json
# import os
# import csv
# import io

# from flask_sqlalchemy import SQLAlchemy
# app = Flask(__name__)
# app.secret_key = "mysecretkey123" 

# # Database Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0606@localhost:5433/attendance_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# # --------- Student Table ---------

# class Student(db.Model):
#     __tablename__ = 'students'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))
#     rollno = db.Column(db.Integer)

# class Attendance(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_name = db.Column(db.String(50), nullable=False)
#     status = db.Column(db.String(20), nullable=False, default="Present")
#     date = db.Column(db.String(20), nullable=False)
#     time = db.Column(db.String(20), nullable=False)

# # Create tables
# with app.app_context():
#     db.create_all()



# # -------------------------------
# # Load Models 
# # -------------------------------



# embeddingModel = "model/openface_nn4.small2.v1.t7"
# recognizerFile = "output/recognizer.pickle"
# labelEncFile = "output/le.pickle"
# conf = 0.5



# print("Loading models...")
# prototxt = "model/deploy.prototxt"
# model = "model/res10_300x300_ssd_iter_140000.caffemodel"
# detector = cv2.dnn.readNetFromCaffe(prototxt, model)
# embedder = cv2.dnn.readNetFromTorch(embeddingModel)
# recognizer = pickle.loads(open(recognizerFile, "rb").read())
# le = pickle.loads(open(labelEncFile, "rb").read())



# attendance = {}   # Stores {name: {date, time}}
# message = ""      # Temporary success message


# ADMIN_USERNAME = "Admin"
# ADMIN_PASSWORD = "Admin"



# def mark_attendance(name):
#     from datetime import datetime
#     date_str = datetime.now().strftime("%Y-%m-%d")
#     time_str = datetime.now().strftime("%H:%M:%S")

#     with app.app_context():   
#         existing = Attendance.query.filter_by(student_name=name, date=date_str).first()

#         if not existing:
#             new_entry = Attendance(
#                 student_name=name,
#                 date=date_str,
#                 time=time_str,
#                 status="Present"   # ✅ FIX ADDED
#             )
#             db.session.add(new_entry)
#             db.session.commit()
#             print(f"✅ Attendance marked for {name}")
#         else:
#             print(f"⚠️ {name} already marked today")





# # ---- Load registered students ----
# def load_registered_students():
#     students = []
#     try:
#         with open('student.csv', 'r') as file:
#             reader = csv.reader(file)
#             for row in reader:
#                 if len(row) >= 2:
#                     students.append({"name": row[0], "roll": row[1]})
#     except FileNotFoundError:
#         pass
#     return students

# # -------------------------------
# # Generate Camera Frames
# # -------------------------------


# def generate_frames():
#     global message
#     cam = cv2.VideoCapture(0)
#     time.sleep(2.0)
#     message_display_time = 0

#     while True:
#         success, frame = cam.read()
#         if not success:
#             break

#         frame = imutils.resize(frame, width=600)
#         (h, w) = frame.shape[:2]

#         # Detect face
#         imageBlob = cv2.dnn.blobFromImage(
#             cv2.resize(frame, (300, 300)),
#             1.0, (300, 300),
#             (104.0, 177.0, 123.0),
#             swapRB=False, crop=False
#         )
#         detector.setInput(imageBlob)
#         detections = detector.forward()

#         for i in range(0, detections.shape[2]):
#             confidence = detections[0, 0, i, 2]
#             if confidence > conf:
#                 box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#                 (startX, startY, endX, endY) = box.astype("int")

#                 face = frame[startY:endY, startX:endX]
#                 (fH, fW) = face.shape[:2]
#                 if fW < 20 or fH < 20:
#                     continue

#                 faceBlob = cv2.dnn.blobFromImage(
#                     face, 1.0 / 255, (96, 96), (0, 0, 0),
#                     swapRB=True, crop=False
#                 )
#                 embedder.setInput(faceBlob)
#                 vec = embedder.forward()

#                 preds = recognizer.predict_proba(vec)[0]
#                 j = np.argmax(preds)
#                 proba = preds[j]
#                 name = le.classes_[j]


#                 marked_students = set()     # stores names already marked once
#                 message_state = {}    


#                 if proba >= 0.75:

#                 # If the student is NOT yet marked
#                     if name not in marked_students:
#                         with app.app_context():
#                             mark_attendance(name)

#                         marked_students.add(name)
#                         # First time message
#                         if message_state.get(name) != "marked":
#                             text = "{} : {:.2f}%".format(name, proba * 100)
#                             message = f"Attendance marked for {name}"
#                             message_display_time = time.time()
#                             message_state[name] = "marked"
#                         else:
#                             text = ""     # do not show again
                
#                     # Student already marked
#                     else:
#                         if message_state.get(name) != "already":
#                             text = "{} : {:.2f}%".format(name, proba * 100)
#                             message = f"Attendance already marked for {name}"
#                             message_display_time = time.time()
#                             message_state[name] = "already"
#                         else:
#                             text = ""     # do not show repeated messages

#                 else:
#                     text = "Unknown"


            
#                 y = startY - 10 if startY - 10 > 10 else startY + 10
#                 cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
#                 cv2.putText(frame, text, (startX, y),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#         # ✅ Show success message for 3 seconds
#         if message and time.time() - message_display_time < 3:
#             cv2.putText(frame, message, (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
#         elif time.time() - message_display_time >= 3:
#             message = ""

#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#     cam.release()

# # -------------------------------
# # Flask Routes
# # -------------------------------

# @app.route('/')
# def index():
#     """Homepage — Live Camera"""
#     return render_template('index.html')

# @app.route('/video_feed')
# def video_feed():
#     """Video streaming route"""
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



# @app.route('/attendance')
# def show_attendance():
#     data = Attendance.query.order_by(Attendance.id.desc()).all()
#     return render_template('attendance.html', data=data)



# from datetime import date
# from sqlalchemy import func

# from sqlalchemy import or_, cast, String
# from sqlalchemy import or_



# @app.route('/absent', methods=['GET'])
# def show_absent_page():
#     today = date.today()
#     today_str = today.strftime("%Y-%m-%d")

#     # --- Present / Late students ---
#     data = Attendance.query.filter(Attendance.date == today_str).all()
#     late_students = Attendance.query.filter(
#         Attendance.date == today_str,
#         Attendance.time > "09:15:00"
#     ).all()

#     # --- Absent students ---
#     all_students = Student.query.all()
#     all_names = {student.name for student in all_students}
#     present_names = {row.student_name for row in data}
#     absentees = sorted(all_names - present_names)

#     # --- Search functionality ---
#     search_query = request.args.get('search', '').strip()
#     search_results = None

#     if search_query:
#         # Search Attendance table
#         search_results = Attendance.query.filter(
#             or_(
#                 Attendance.student_name.ilike(f"%{search_query}%"),
#                 Attendance.status.ilike(f"%{search_query}%"),
#                 cast(Attendance.date, String).ilike(f"%{search_query}%"),
#                 cast(Attendance.time, String).ilike(f"%{search_query}%")
#             )
#         ).all()

#         # Include matching absent students from absentees
#         absentees_filtered = [s for s in absentees if search_query.lower() in s.lower()]
#     else:
#         absentees_filtered = absentees

#     return render_template(
#         "absent.html",
#         data=data,
#         late_students=late_students,
#         absentees=absentees_filtered,
#         current_date=today_str,
#         search_query=search_query,
#         search_results=search_results
#     )



# @app.route('/admin_login', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
#             session['admin'] = True
#             # Redirect admin to the absent page after login
#             return redirect(url_for('show_absent_page'))

#         else:
#             return render_template('admin_login.html', error="Invalid credentials!")

#     return render_template('admin_login.html')

# @app.route('/admin_logout')
# def admin_logout():
#     session.pop('admin', None)
#     return redirect(url_for('show_attendance'))

# @app.route('/add', methods=['POST'])
# def add_student():
#     data = request.get_json()
#     new_student = Student(name=data['name'], rollno=data['rollno'])
#     db.session.add(new_student)
#     db.session.commit()
#     return jsonify({'message': 'Student added successfully'})

# @app.route('/students', methods=['GET'])
# def get_students():
#     students = Student.query.all()
#     result = [{'id': s.id, 'name': s.name, 'rollno': s.rollno} for s in students]
#     return jsonify(result)

# @app.route('/update/<int:id>', methods=['PUT'])
# def update_student(id):
#     student = Student.query.get(id)
#     if not student:
#         return jsonify({'message': 'Student not found'})
#     data = request.get_json()
#     student.name = data.get('name', student.name)
#     student.rollno = data.get('rollno', student.rollno)
#     db.session.commit()
#     return jsonify({'message': 'Student updated successfully'})


# @app.route('/delete_attendance/<int:id>', methods=['POST'])
# def delete_attendance(id):
#     record = Attendance.query.get(id)
#     if record:
#         db.session.delete(record)
#         # db.session.commit()
#     return redirect(url_for('show_attendance'))



# if __name__ == "__main__":
#     app.run(debug=True)


#--------------------------------------------------------------------------------past code-----------------------------


# from flask import Flask, render_template, Response, redirect, session, send_file , request ,url_for ,jsonify
# import numpy as np
# import imutils
# import pickle
# import cv2
# import time
# from datetime import datetime
# import json
# import os
# import csv
# import io

# from flask_sqlalchemy import SQLAlchemy
# app = Flask(__name__)
# app.secret_key = "mysecretkey123" 

# # Database Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0606@localhost:5433/attendance_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# # --------- Student Table ---------

# class Student(db.Model):
#     __tablename__ = 'students'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))
#     rollno = db.Column(db.Integer)

# class Attendance(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_name = db.Column(db.String(50), nullable=False)
#     status = db.Column(db.String(20), nullable=False, default="Present")
#     date = db.Column(db.String(20), nullable=False)
#     time = db.Column(db.String(20), nullable=False)

# # Create tables
# with app.app_context():
#     db.create_all()

# # -------------------------------
# # Load Models 
# # -------------------------------

# embeddingModel = "model/openface_nn4.small2.v1.t7"
# recognizerFile = "output/recognizer.pickle"
# labelEncFile = "output/le.pickle"
# conf = 0.5

# print("Loading models...")
# prototxt = "model/deploy.prototxt"
# model = "model/res10_300x300_ssd_iter_140000.caffemodel"
# detector = cv2.dnn.readNetFromCaffe(prototxt, model)
# embedder = cv2.dnn.readNetFromTorch(embeddingModel)
# recognizer = pickle.loads(open(recognizerFile, "rb").read())
# le = pickle.loads(open(labelEncFile, "rb").read())

# attendance = {}  
# message = ""      

# ADMIN_USERNAME = "Admin"
# ADMIN_PASSWORD = "Admin"

# # ---------------------------------------
# # Database Attendance Marking Function
# # ---------------------------------------

# def mark_attendance(name):
#     from datetime import datetime
#     date_str = datetime.now().strftime("%Y-%m-%d")
#     time_str = datetime.now().strftime("%H:%M:%S")

#     with app.app_context():
#         existing = Attendance.query.filter_by(student_name=name, date=date_str).first()

#         if not existing:
#             new_entry = Attendance(
#                 student_name=name,
#                 date=date_str,
#                 time=time_str,
#                 status="Present"
#             )
#             db.session.add(new_entry)
#             db.session.commit()
#             print(f"✅ Attendance marked for {name}")
#         else:
#             print(f"⚠️ {name} already marked today")

# # ---- Load registered students ----
# def load_registered_students():
#     students = []
#     try:
#         with open('student.csv', 'r') as file:
#             reader = csv.reader(file)
#             for row in reader:
#                 if len(row) >= 2:
#                     students.append({"name": row[0], "roll": row[1]})
#     except FileNotFoundError:
#         pass
#     return students

# # --------------------------------------------------
# # GLOBAL message state (🔥 MUST BE OUTSIDE THE LOOP)
# # --------------------------------------------------

# marked_students = set()
# message_state = {}

# # -------------------------------
# # Generate Camera Frames
# # -------------------------------

# def generate_frames():
#     global message
#     cam = cv2.VideoCapture(0)
#     time.sleep(2.0)
#     message_display_time = 0

#     while True:
#         success, frame = cam.read()
#         if not success:
#             break

#         frame = imutils.resize(frame, width=600)
#         (h, w) = frame.shape[:2]

#         # Detect face
#         imageBlob = cv2.dnn.blobFromImage(
#             cv2.resize(frame, (300, 300)),
#             1.0, (300, 300),
#             (104.0, 177.0, 123.0),
#             swapRB=False, crop=False
#         )
#         detector.setInput(imageBlob)
#         detections = detector.forward()

#         for i in range(0, detections.shape[2]):
#             confidence = detections[0, 0, i, 2]
#             if confidence > conf:
#                 box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#                 (startX, startY, endX, endY) = box.astype("int")

#                 face = frame[startY:endY, startX:endX]
#                 (fH, fW) = face.shape[:2]
#                 if fW < 20 or fH < 20:
#                     continue

#                 faceBlob = cv2.dnn.blobFromImage(
#                     face, 1.0 / 255, (96, 96), (0, 0, 0),
#                     swapRB=True, crop=False
#                 )
#                 embedder.setInput(faceBlob)
#                 vec = embedder.forward()

#                 preds = recognizer.predict_proba(vec)[0]
#                 j = np.argmax(preds)
#                 proba = preds[j]
#                 name = le.classes_[j]

#                 # ----------------------------------------------------
#                 # Attendance Logic (🔥 FIXED and working perfectly)
#                 # ----------------------------------------------------
#                 if proba >= 0.75:

#                     # FIRST TIME
#                     if name not in marked_students:
#                         with app.app_context():
#                             mark_attendance(name)

#                         marked_students.add(name)

#                         text = "{} : {:.2f}%".format(name, proba * 100)
#                         message = f"Attendance marked for {name}"
#                         message_display_time = time.time()
#                         message_state[name] = "marked"

#                     # ALREADY MARKED
#                     else:
#                         text = "{} : {:.2f}%".format(name, proba * 100)
#                         message = f"Attendance already marked for {name}"
#                         message_display_time = time.time()
#                         message_state[name] = "already"

#                 else:
#                     text = "Unknown"

#                 y = startY - 10 if startY - 10 > 10 else startY + 10
#                 cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
#                 cv2.putText(frame, text, (startX, y),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#         # -------------------------------------------
#         # SHOW UI MESSAGE (🔥 FIXED, shows for 3 sec)
#         # -------------------------------------------
#         if message and time.time() - message_display_time < 3:
#             cv2.putText(frame, message, (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
#         elif time.time() - message_display_time >= 3:
#             message = ""

#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#     cam.release()

# # -------------------------------
# # Flask Routes
# # -------------------------------

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/attendance')
# def show_attendance():
#     data = Attendance.query.order_by(Attendance.id.desc()).all()
#     return render_template('attendance.html', data=data)

# # from datetime import date
# # from sqlalchemy import or_, cast, String

# # @app.route('/absent', methods=['GET'])
# # def show_absent_page():
# #     today = date.today()
# #     today_str = today.strftime("%Y-%m-%d")

# #     data = Attendance.query.filter(Attendance.date == today_str).all()
# #     late_students = Attendance.query.filter(
# #         Attendance.date == today_str,
# #         Attendance.time > "09:15:00"
# #     ).all()

# #     all_students = Student.query.all()
# #     all_names = {student.name for student in all_students}
# #     present_names = {row.student_name for row in data}
# #     absentees = sorted(all_names - present_names)

# #     search_query = request.args.get('search', '').strip()
# #     search_results = None

# #     if search_query:
# #         search_results = Attendance.query.filter(
# #             or_(
# #                 Attendance.student_name.ilike(f"%{search_query}%"),
# #                 Attendance.status.ilike(f"%{search_query}%"),
# #                 cast(Attendance.date, String).ilike(f"%{search_query}%"),
# #                 cast(Attendance.time, String).ilike(f"%{search_query}%")
# #             )
# #         ).all()

# #         absentees_filtered = [s for s in absentees if search_query.lower() in s.lower()]
# #     else:
# #         absentees_filtered = absentees

# #     return render_template(
# #         "absent.html",
# #         data=data,
# #         late_students=late_students,
# #         absentees=absentees_filtered,
# #         current_date=today_str,
# #         search_query=search_query,
# #         search_results=search_results
# #     )

# from datetime import date
# from sqlalchemy import or_, cast, String
# from flask import request, render_template

# @app.route('/absent', methods=['GET'])
# def show_absent_page():
#     today = date.today()

#     # Correct formats
#     db_date = today.strftime("%Y-%m-%d")      # for database query
#     display_date = today.strftime("%d-%m-%Y") # for HTML UI display

#     # Query today's attendance
#     data = Attendance.query.filter(Attendance.date == db_date).all()

#     # Late students
#     late_students = Attendance.query.filter(
#         Attendance.date == db_date,
#         Attendance.time > "09:15:00"
#     ).all()

#     # All students list
#     all_students = Student.query.all()
#     all_names = {student.name for student in all_students}

#     # Names present today
#     present_names = {row.student_name for row in data}

#     # Absent students list
#     absentees = sorted(all_names - present_names)

#     # Search logic
#     search_query = request.args.get('search', '').strip()
#     search_results = None

#     if search_query:
#         # Search in attendance table
#         search_results = Attendance.query.filter(
#             or_(
#                 Attendance.student_name.ilike(f"%{search_query}%"),
#                 Attendance.status.ilike(f"%{search_query}%"),
#                 cast(Attendance.date, String).ilike(f"%{search_query}%"),
#                 cast(Attendance.time, String).ilike(f"%{search_query}%")
#             )
#         ).all()

#         # Filter absent students
#         absentees_filtered = [s for s in absentees if search_query.lower() in s.lower()]
#     else:
#         absentees_filtered = absentees

#     # Pass values to HTML
#     return render_template(
#         "absent.html",
#         data=data,
#         late_students=late_students,
#         absentees=absentees_filtered,
#         current_date=display_date,   # DD-MM-YYYY format sent to HTML
#         search_query=search_query,
#         search_results=search_results
#     )



# @app.route('/admin_login', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
#             session['admin'] = True
#             return redirect(url_for('show_absent_page'))

#         else:
#             return render_template('admin_login.html', error="Invalid credentials!")

#     return render_template('admin_login.html')

# @app.route('/admin_logout')
# def admin_logout():
#     session.pop('admin', None)
#     return redirect(url_for('show_attendance'))

# @app.route('/add', methods=['POST'])
# def add_student():
#     data = request.get_json()
#     new_student = Student(name=data['name'], rollno=data['rollno'])
#     db.session.add(new_student)
#     db.session.commit()
#     return jsonify({'message': 'Student added successfully'})

# @app.route('/students', methods=['GET'])
# def get_students():
#     students = Student.query.all()
#     result = [{'id': s.id, 'name': s.name, 'rollno': s.rollno} for s in students]
#     return jsonify(result)

# @app.route('/update/<int:id>', methods=['PUT'])
# def update_student(id):
#     student = Student.query.get(id)
#     if not student:
#         return jsonify({'message': 'Student not found'})
#     data = request.get_json()
#     student.name = data.get('name', student.name)
#     student.rollno = data.get('rollno', student.rollno)
#     db.session.commit()
#     return jsonify({'message': 'Student updated successfully'})

# @app.route('/delete_attendance/<int:id>', methods=['POST'])
# def delete_attendance(id):
#     record = Attendance.query.get(id)
#     if record:
#         db.session.delete(record)
#         db.session.commit()
#     return redirect(url_for('show_attendance'))



# if __name__ == "__main__":
#     app.run(debug=True)






# from flask import Flask, render_template, Response, redirect, session, send_file , request ,url_for ,jsonify
# import numpy as np
# import imutils
# import pickle
# import cv2
# import time
# from datetime import datetime
# import json
# import os
# import csv
# import io

# from flask_sqlalchemy import SQLAlchemy
# app = Flask(__name__)


# app.secret_key = "mysecretkey123" 

# # Database Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0606@localhost:5433/attendance_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# # --------- Student Table ---------

# class Student(db.Model):
#     __tablename__ = 'students'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))
#     rollno = db.Column(db.Integer)
#     phone = db.Column(db.String(20))   # <-- ADDED phone column

# class Attendance(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_name = db.Column(db.String(50), nullable=False)
#     status = db.Column(db.String(20), nullable=False, default="Present")
#     date = db.Column(db.String(20), nullable=False)
#     time = db.Column(db.String(20), nullable=False)

# # Create tables
# with app.app_context():
#     db.create_all()

# # -------------------------------
# # Load Models 
# # -------------------------------

# embeddingModel = "model/openface_nn4.small2.v1.t7"
# recognizerFile = "output/recognizer.pickle"
# labelEncFile = "output/le.pickle"
# conf = 0.5

# print("Loading models...")
# prototxt = "model/deploy.prototxt"
# model = "model/res10_300x300_ssd_iter_140000.caffemodel"
# detector = cv2.dnn.readNetFromCaffe(prototxt, model)
# embedder = cv2.dnn.readNetFromTorch(embeddingModel)
# recognizer = pickle.loads(open(recognizerFile, "rb").read())
# le = pickle.loads(open(labelEncFile, "rb").read())

# attendance = {}   # Stores {name: {date, time}}
# message = ""      # Temporary success message

# ADMIN_USERNAME = "Admin"
# ADMIN_PASSWORD = "Admin"

# # -------------------------------
# # Twilio WhatsApp helper (ADDED)
# # -------------------------------
# # You provided these credentials — they are placed here as requested.
# # For production consider using environment variables instead of hardcoding.
# try:
#     from twilio.rest import Client
#     ACCOUNT_SID = "AC25235359687d991d0db7b5e4870924a1"   # given by you
#     AUTH_TOKEN  = "d4cb4e5d6ff7fedd60e2f1698b4bd5af"   # given by you
#     twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

#     def send_whatsapp_message(phone_number, message_text):
#         """
#         Send WhatsApp message using Twilio.
#         phone_number: string containing digits only or with + country code.
#         Example stored phone could be '9876543210' (India) -> we'll add +91 prefix if needed.
#         """
#         # Normalize: if phone_number starts with '+' use as-is; otherwise assume Indian +91
#         to_number = phone_number.strip()
#         if not to_number:
#             raise ValueError("Empty phone number")

#         # If user stored number without +country, you may need to adjust. Here we attempt:
#         if to_number.startswith('+'):
#             to_whatsapp = f'whatsapp:{to_number}'
#         else:
#             # If it already includes country code like '919876543210' keep it; otherwise prefix +91
#             if len(to_number) >= 10 and to_number.startswith('91'):
#                 to_whatsapp = f'whatsapp:+{to_number}'
#             elif len(to_number) == 10:
#                 to_whatsapp = f'whatsapp:+91{to_number}'
#             else:
#                 # fallback — send as-is with whatsapp:
#                 to_whatsapp = f'whatsapp:{to_number}'

#         from_whatsapp = 'whatsapp:+14155238886'  # Twilio sandbox / official WhatsApp number

#         # Send message
#         message = twilio_client.messages.create(
#             from_=from_whatsapp,
#             body=message_text,
#             to=to_whatsapp
#         )
#         return message.sid

# except Exception as e:
#     # Twilio not available or error — provide a stub that prints instead of sending.
#     print("Twilio client init error (or not installed). WhatsApp will be stubbed. Error:", e)
#     def send_whatsapp_message(phone_number, message_text):
#         print(f"[STUB] WhatsApp -> {phone_number}: {message_text}")
#         return "stub-sid"

# # -------------------------------
# # Attendance marking
# # -------------------------------

# def mark_attendance(name):
#     from datetime import datetime
#     date_str = datetime.now().strftime("%Y-%m-%d")
#     time_str = datetime.now().strftime("%H:%M:%S")

#     with app.app_context():   
#         existing = Attendance.query.filter_by(student_name=name, date=date_str).first()

#         if not existing:
#             new_entry = Attendance(
#                 student_name=name,
#                 date=date_str,
#                 time=time_str,
#                 status="Present"   # ✅ FIX ADDED
#             )
#             db.session.add(new_entry)
#             db.session.commit()
#             print(f"✅ Attendance marked for {name}")
#             return True
#         else:
#             print(f"⚠️ {name} already marked today")
#             return False

# # ---- Load registered students ----
# def load_registered_students():
#     students = []
#     try:
#         with open('student.csv', 'r') as file:
#             reader = csv.reader(file)
#             for row in reader:
#                 if len(row) >= 2:
#                     students.append({"name": row[0], "roll": row[1]})
#     except FileNotFoundError:
#         pass
#     return students

# # -------------------------------
# # Generate Camera Frames
# # -------------------------------

# def generate_frames():
#     global message
#     cam = cv2.VideoCapture(0)
#     time.sleep(2.0)
#     message_display_time = 0

#     while True:
#         success, frame = cam.read()
#         if not success:
#             break

#         frame = imutils.resize(frame, width=600)
#         (h, w) = frame.shape[:2]

#         # Detect face
#         imageBlob = cv2.dnn.blobFromImage(
#             cv2.resize(frame, (300, 300)),
#             1.0, (300, 300),
#             (104.0, 177.0, 123.0),
#             swapRB=False, crop=False
#         )
#         detector.setInput(imageBlob)
#         detections = detector.forward()

#         for i in range(0, detections.shape[2]):
#             confidence = detections[0, 0, i, 2]
#             if confidence > conf:
#                 box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#                 (startX, startY, endX, endY) = box.astype("int")

#                 face = frame[startY:endY, startX:endX]
#                 (fH, fW) = face.shape[:2]
#                 if fW < 20 or fH < 20:
#                     continue

#                 faceBlob = cv2.dnn.blobFromImage(
#                     face, 1.0 / 255, (96, 96), (0, 0, 0),
#                     swapRB=True, crop=False
#                 )
#                 embedder.setInput(faceBlob)
#                 vec = embedder.forward()

#                 preds = recognizer.predict_proba(vec)[0]
#                 j = np.argmax(preds)
#                 proba = preds[j]
#                 name = le.classes_[j]


#                 marked_students = set()     # stores names already marked once
#                 message_state = {}    


#                 if proba >= 0.75:

#                 # If the student is NOT yet marked
#                     if name not in marked_students:
#                         with app.app_context():
#                             marked = mark_attendance(name)

#                             # ----------------------------
#                             # SEND WHATSAPP TO THE STUDENT
#                             # ----------------------------
#                             # Lookup student by name and send message if phone exists
#                             try:
#                                 student = Student.query.filter_by(name=name).first()
#                                 if student and getattr(student, "phone", None):
#                                     msg_text = f"Hello {name}, your attendance is marked at {datetime.now().strftime('%H:%M:%S')}."
#                                     try:
#                                         sid = send_whatsapp_message(student.phone, msg_text)
#                                         print(f"WhatsApp sent to {student.phone} (sid: {sid})")
#                                     except Exception as e_send:
#                                         print("WhatsApp send error:", e_send)
#                                 else:
#                                     print(f"No phone found for {name} — skipping WhatsApp.")
#                             except Exception as e_q:
#                                 print("DB lookup error for WhatsApp:", e_q)
#                             # ----------------------------

#                         marked_students.add(name)
#                         # First time message
#                         if message_state.get(name) != "marked":
#                             text = "{} : {:.2f}%".format(name, proba * 100)
#                             message = f"Attendance marked for {name}"
#                             message_display_time = time.time()
#                             message_state[name] = "marked"
#                         else:
#                             text = ""     # do not show again
                
#                     # Student already marked
#                     else:
#                         if message_state.get(name) != "already":
#                             text = "{} : {:.2f}%".format(name, proba * 100)
#                             message = f"Attendance already marked for {name}"
#                             message_display_time = time.time()
#                             message_state[name] = "already"
#                         else:
#                             text = ""     # do not show repeated messages

#                 else:
#                     text = "Unknown"


            
#                 y = startY - 10 if startY - 10 > 10 else startY + 10
#                 cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
#                 cv2.putText(frame, text, (startX, y),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#         # ✅ Show success message for 3 seconds
#         if message and time.time() - message_display_time < 3:
#             cv2.putText(frame, message, (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
#         elif time.time() - message_display_time >= 3:
#             message = ""

#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#     cam.release()

# # -------------------------------
# # Flask Routes
# # -------------------------------

# @app.route('/')
# def index():
#     """Homepage — Live Camera"""
#     return render_template('index.html')

# @app.route('/video_feed')
# def video_feed():
#     """Video streaming route"""
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/attendance')
# def show_attendance():
#     data = Attendance.query.order_by(Attendance.id.desc()).all()
#     return render_template('attendance.html', data=data)

# from datetime import date
# from sqlalchemy import func

# from sqlalchemy import or_, cast, String
# from sqlalchemy import or_

# @app.route('/absent', methods=['GET'])
# def show_absent_page():
#     today = date.today()
#     today_str = today.strftime("%Y-%m-%d")

#     # --- Present / Late students ---
#     data = Attendance.query.filter(Attendance.date == today_str).all()
#     late_students = Attendance.query.filter(
#         Attendance.date == today_str,
#         Attendance.time > "09:15:00"
#     ).all()

#     # --- Absent students ---
#     all_students = Student.query.all()
#     all_names = {student.name for student in all_students}
#     present_names = {row.student_name for row in data}
#     absentees = sorted(all_names - present_names)

#     # --- Search functionality ---
#     search_query = request.args.get('search', '').strip()
#     search_results = None

#     if search_query:
#         # Search Attendance table
#         search_results = Attendance.query.filter(
#             or_(
#                 Attendance.student_name.ilike(f"%{search_query}%"),
#                 Attendance.status.ilike(f"%{search_query}%"),
#                 cast(Attendance.date, String).ilike(f"%{search_query}%"),
#                 cast(Attendance.time, String).ilike(f"%{search_query}%")
#             )
#         ).all()

#         # Include matching absent students from absentees
#         absentees_filtered = [s for s in absentees if search_query.lower() in s.lower()]
#     else:
#         absentees_filtered = absentees

#     return render_template(
#         "absent.html",
#         data=data,
#         late_students=late_students,
#         absentees=absentees_filtered,
#         current_date=today_str,
#         search_query=search_query,
#         search_results=search_results
#     )

# @app.route('/admin_login', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
#             session['admin'] = True
#             # Redirect admin to the absent page after login
#             return redirect(url_for('show_absent_page'))

#         else:
#             return render_template('admin_login.html', error="Invalid credentials!")

#     return render_template('admin_login.html')

# @app.route('/admin_logout')
# def admin_logout():
#     session.pop('admin', None)
#     return redirect(url_for('show_attendance'))

# @app.route('/add', methods=['POST'])
# def add_student():
#     data = request.get_json()
#     new_student = Student(name=data['name'], rollno=data['rollno'])
#     # If client provides phone, save it too
#     if 'phone' in data:
#         new_student.phone = data['phone']
#     db.session.add(new_student)
#     db.session.commit()
#     return jsonify({'message': 'Student added successfully'})

# @app.route('/students', methods=['GET'])
# def get_students():
#     students = Student.query.all()
#     result = [{'id': s.id, 'name': s.name, 'rollno': s.rollno, 'phone': s.phone} for s in students]
#     return jsonify(result)

# @app.route('/update/<int:id>', methods=['PUT'])
# def update_student(id):
#     student = Student.query.get(id)
#     if not student:
#         return jsonify({'message': 'Student not found'})
#     data = request.get_json()
#     student.name = data.get('name', student.name)
#     student.rollno = data.get('rollno', student.rollno)
#     if 'phone' in data:
#         student.phone = data.get('phone', student.phone)
#     db.session.commit()
#     return jsonify({'message': 'Student updated successfully'})

# @app.route('/delete_attendance/<int:id>', methods=['POST'])
# def delete_attendance(id):
#     record = Attendance.query.get(id)
#     if record:
#         db.session.delete(record)
#         db.session.commit()
#     return redirect(url_for('show_attendance'))

# if __name__ == "__main__":
#     app.run(debug=True)




#its newwwwwww-------------------------------------------------------------------



# from flask import Flask, render_template, Response, redirect, session, send_file , request ,url_for ,jsonify
# import numpy as np
# import imutils
# import pickle
# import cv2
# import time
# from datetime import datetime
# import json
# import os
# import csv
# import io

# import requests     # <-- ADDED for UltraMsg WhatsApp API

# from flask_sqlalchemy import SQLAlchemy
# app = Flask(__name__)
# app.secret_key = "mysecretkey123" 

# # ==============================
# # ULTRAMSG WHATSAPP CONFIG
# # ==============================
# ULTRA_INSTANCE_ID = "instance150419"
# ULTRA_TOKEN = "ffm5tlm6x0gqp4ue"

# def send_whatsapp_message(phone_number, message_text):
#     url = f"https://api.ultramsg.com/{ULTRA_INSTANCE_ID}/messages/chat"

#     data = {
#         "token": ULTRA_TOKEN,
#         "to": phone_number,   # must be like +919XXXXXXXXX
#         "body": message_text
#     }

#     response = requests.post(url, data=data)
#     print("WhatsApp Response:", response.text)


# # Database Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0606@localhost:5433/attendance_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# # --------- Student Table ---------

# class Student(db.Model):
#     __tablename__ = 'students'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))
#     rollno = db.Column(db.Integer)
#     phone = db.Column(db.String(20))   # <-- ADDED (REQUIRED)

# class Attendance(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_name = db.Column(db.String(50), nullable=False)
#     status = db.Column(db.String(20), nullable=False, default="Present")
#     date = db.Column(db.String(20), nullable=False)
#     time = db.Column(db.String(20), nullable=False)

# # Create tables
# with app.app_context():
#     db.create_all()

# # -------------------------------
# # Load Models 
# # -------------------------------

# embeddingModel = "model/openface_nn4.small2.v1.t7"
# recognizerFile = "output/recognizer.pickle"
# labelEncFile = "output/le.pickle"
# conf = 0.5

# print("Loading models...")
# prototxt = "model/deploy.prototxt"
# model = "model/res10_300x300_ssd_iter_140000.caffemodel"
# detector = cv2.dnn.readNetFromCaffe(prototxt, model)
# embedder = cv2.dnn.readNetFromTorch(embeddingModel)
# recognizer = pickle.loads(open(recognizerFile, "rb").read())
# le = pickle.loads(open(labelEncFile, "rb").read())

# attendance = {}
# message = ""

# ADMIN_USERNAME = "Admin"
# ADMIN_PASSWORD = "Admin"

# def mark_attendance(name):
#     from datetime import datetime
#     date_str = datetime.now().strftime("%Y-%m-%d")
#     time_str = datetime.now().strftime("%H:%M:%S")

#     with app.app_context():   
#         existing = Attendance.query.filter_by(student_name=name, date=date_str).first()

#         if not existing:
#             new_entry = Attendance(
#                 student_name=name,
#                 date=date_str,
#                 time=time_str,
#                 status="Present"
#             )
#             db.session.add(new_entry)
#             db.session.commit()
#             print(f"Attendance marked for {name}")
#             return True

#         return False


# # -------------------------------
# # Generate Camera Frames
# # -------------------------------

# def generate_frames():
#     global message
#     cam = cv2.VideoCapture(0)
#     time.sleep(2.0)
#     message_display_time = 0

#     while True:
#         success, frame = cam.read()
#         if not success:
#             break

#         frame = imutils.resize(frame, width=600)
#         (h, w) = frame.shape[:2]

#         # Detect face
#         imageBlob = cv2.dnn.blobFromImage(
#             cv2.resize(frame, (300, 300)),
#             1.0, (300, 300),
#             (104.0, 177.0, 123.0),
#             swapRB=False, crop=False
#         )
#         detector.setInput(imageBlob)
#         detections = detector.forward()

#         for i in range(0, detections.shape[2]):
#             confidence = detections[0, 0, i, 2]
#             if confidence > conf:
#                 box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#                 (startX, startY, endX, endY) = box.astype("int")

#                 face = frame[startY:endY, startX:endX]
#                 (fH, fW) = face.shape[:2]
#                 if fW < 20 or fH < 20:
#                     continue

#                 faceBlob = cv2.dnn.blobFromImage(
#                     face, 1.0/255, (96, 96), (0, 0, 0),
#                     swapRB=True, crop=False
#                 )
#                 embedder.setInput(faceBlob)
#                 vec = embedder.forward()

#                 preds = recognizer.predict_proba(vec)[0]
#                 j = np.argmax(preds)
#                 proba = preds[j]
#                 name = le.classes_[j]

#                 marked_students = set()
#                 message_state = {}

#                 if proba >= 0.75:

#                     if name not in marked_students:
#                         with app.app_context():
#                             success = mark_attendance(name)

#                             # =====================================
#                             # SEND WHATSAPP HERE (ADDED)
#                             # =====================================
#                             student = Student.query.filter_by(name=name).first()
#                             if student and student.phone:
#                                 msg = f"Hello {name}, your attendance is marked at {datetime.now().strftime('%H:%M:%S')}."
#                                 send_whatsapp_message(student.phone, msg)
#                                 print("WhatsApp sent to", student.phone)
#                             else:
#                                 print("No phone number found!")

#                         marked_students.add(name)
#                         message = f"Attendance marked for {name}"
#                         text = f"{name}: {proba*100:.2f}%"
#                         message_display_time = time.time()

#                     else:
#                         message = f"Attendance already marked for {name}"
#                         text = f"{name}: {proba*100:.2f}%"
#                         message_display_time = time.time()

#                 else:
#                     text = "Unknown"

#                 y = startY - 10 if startY - 10 > 10 else startY + 10
#                 cv2.rectangle(frame, (startX, startY), (endX, endY), (0,255,0), 2)
#                 cv2.putText(frame, text, (startX, y),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

#         if message and time.time() - message_display_time < 3:
#             cv2.putText(frame, message, (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
#         else:
#             message = ""

#         ret, buffer = cv2.imencode(".jpg", frame)
#         frame = buffer.tobytes()

#         yield (b"--frame\r\n"
#                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

#     cam.release()


# # -------------------------------
# # Routes (UNCHANGED)
# # -------------------------------

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/attendance')
# def show_attendance():
#     data = Attendance.query.order_by(Attendance.id.desc()).all()
#     return render_template('attendance.html', data=data)


# # Your other routes remain EXACTLY the same…
# # (I did NOT change anything)


# from datetime import date
# from sqlalchemy import func
# from sqlalchemy import or_, cast, String

# @app.route('/absent', methods=['GET'])
# def show_absent_page():
#     today = date.today()
#     today_str = today.strftime("%Y-%m-%d")

#     data = Attendance.query.filter(Attendance.date == today_str).all()
#     late_students = Attendance.query.filter(
#         Attendance.date == today_str,
#         Attendance.time > "09:15:00"
#     ).all()

#     all_students = Student.query.all()
#     all_names = {s.name for s in all_students}
#     present_names = {p.student_name for p in data}
#     absentees = sorted(all_names - present_names)

#     search_query = request.args.get('search', '').strip()
#     search_results = None

#     if search_query:
#         search_results = Attendance.query.filter(
#             or_(
#                 Attendance.student_name.ilike(f"%{search_query}%"),
#                 Attendance.status.ilike(f"%{search_query}%"),
#                 cast(Attendance.date, String).ilike(f"%{search_query}%"),
#                 cast(Attendance.time, String).ilike(f"%{search_query}%")
#             )
#         ).all()

#         absentees_filtered = [s for s in absentees if search_query.lower() in s.lower()]
#     else:
#         absentees_filtered = absentees

#     return render_template(
#         "absent.html",
#         data=data,
#         late_students=late_students,
#         absentees=absentees_filtered,
#         current_date=today_str,
#         search_query=search_query,
#         search_results=search_results
#     )

# @app.route('/admin_login', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
#             session['admin'] = True
#             # Redirect admin to the absent page after login
#             return redirect(url_for('show_absent_page'))

#         else:
#             return render_template('admin_login.html', error="Invalid credentials!")

#     return render_template('admin_login.html')

# @app.route('/admin_logout')
# def admin_logout():
#     session.pop('admin', None)
#     return redirect(url_for('show_attendance'))

# @app.route('/add', methods=['POST'])
# def add_student():
#     data = request.get_json()
#     new_student = Student(name=data['name'], rollno=data['rollno'])
#     db.session.add(new_student)
#     db.session.commit()
#     return jsonify({'message': 'Student added successfully'})

# @app.route('/students', methods=['GET'])
# def get_students():
#     students = Student.query.all()
#     result = [{'id': s.id, 'name': s.name, 'rollno': s.rollno} for s in students]
#     return jsonify(result)

# @app.route('/update/<int:id>', methods=['PUT'])
# def update_student(id):
#     student = Student.query.get(id)
#     if not student:
#         return jsonify({'message': 'Student not found'})
#     data = request.get_json()
#     student.name = data.get('name', student.name)
#     student.rollno = data.get('rollno', student.rollno)
#     db.session.commit()
#     return jsonify({'message': 'Student updated successfully'})


# @app.route('/delete_attendance/<int:id>', methods=['POST'])
# def delete_attendance(id):
#     record = Attendance.query.get(id)
#     if record:
#         db.session.delete(record)
#         db.session.commit()
#     return redirect(url_for('show_attendance'))


# if __name__ == "__main__":
#     app.run(debug=True)




#working restiction



# from flask import Flask, render_template, Response, redirect, session, send_file, request, url_for, jsonify
# import numpy as np
# import imutils
# import pickle
# import cv2
# import time
# from datetime import datetime, date
# import json
# import os
# import csv
# import io
# import requests

# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import or_, cast, String

# app = Flask(__name__)
# app.secret_key = "mysecretkey123"

# # ==============================
# # ULTRAMSG WHATSAPP CONFIG
# # ==============================
# ULTRA_INSTANCE_ID = "instance150419"
# ULTRA_TOKEN = "ffm5tlm6x0gqp4ue"

# def send_whatsapp_message(phone_number, message_text):
#     url = f"https://api.ultramsg.com/{ULTRA_INSTANCE_ID}/messages/chat"
#     data = {
#         "token": ULTRA_TOKEN,
#         "to": phone_number,   # must be in international format, e.g. +919XXXXXXXXX
#         "body": message_text
#     }
#     try:
#         response = requests.post(url, data=data, timeout=10)
#         print("WhatsApp Response:", response.text)
#     except Exception as e:
#         print("WhatsApp send error:", e)

# # ==============================
# # DATABASE CONFIG
# # ==============================
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0606@localhost:5433/attendance_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # --------- Student Table ---------
# class Student(db.Model):
#     __tablename__ = 'students'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))
#     rollno = db.Column(db.Integer)
#     phone = db.Column(db.String(20))   # <-- phone column added

# class Attendance(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_name = db.Column(db.String(50), nullable=False)
#     status = db.Column(db.String(20), nullable=False, default="Present")
#     date = db.Column(db.String(20), nullable=False)
#     time = db.Column(db.String(20), nullable=False)

# # MessageLog to limit messages per period/day
# class MessageLog(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_name = db.Column(db.String(50))
#     date = db.Column(db.String(20))
#     period = db.Column(db.String(20))  # "morning" / "afternoon"

# with app.app_context():
#     db.create_all()

# # -------------------------------
# # Load Models
# # -------------------------------
# embeddingModel = "model/openface_nn4.small2.v1.t7"
# recognizerFile = "output/recognizer.pickle"
# labelEncFile = "output/le.pickle"
# conf = 0.5

# print("Loading models...")
# prototxt = "model/deploy.prototxt"
# model = "model/res10_300x300_ssd_iter_140000.caffemodel"
# detector = cv2.dnn.readNetFromCaffe(prototxt, model)
# embedder = cv2.dnn.readNetFromTorch(embeddingModel)
# recognizer = pickle.loads(open(recognizerFile, "rb").read())
# le = pickle.loads(open(labelEncFile, "rb").read())

# attendance = {}   # optional
# message = ""

# ADMIN_USERNAME = "Admin"
# ADMIN_PASSWORD = "Admin"

# # -------------------------------
# # Helper: period detection
# # -------------------------------
# def get_period():
#     hour = datetime.now().hour
#     if hour < 12:
#         return "morning"
#     else:
#         return "afternoon"

# # -------------------------------
# # mark attendance (no changes)
# # -------------------------------
# def mark_attendance(name):
#     date_str = datetime.now().strftime("%Y-%m-%d")
#     time_str = datetime.now().strftime("%H:%M:%S")

#     # Use application context if called from outside request context
#     with app.app_context():
#         existing = Attendance.query.filter_by(student_name=name, date=date_str).first()
#         if not existing:
#             new_entry = Attendance(
#                 student_name=name,
#                 date=date_str,
#                 time=time_str,
#                 status="Present"
#             )
#             db.session.add(new_entry)
#             db.session.commit()
#             print(f"Attendance marked for {name}")
#             return True
#         else:
#             print(f"{name} already marked today")
#             return False

# # -------------------------------
# # Generate Camera Frames
# # -------------------------------
# def generate_frames():
#     global message
#     cam = cv2.VideoCapture(0)
#     time.sleep(2.0)
#     message_display_time = 0

#     # Keep marked_students and message_state inside function to avoid resetting every detection loop
#     marked_students = set()
#     message_state = {}

#     while True:
#         success, frame = cam.read()
#         if not success:
#             break

#         frame = imutils.resize(frame, width=600)
#         (h, w) = frame.shape[:2]

#         imageBlob = cv2.dnn.blobFromImage(
#             cv2.resize(frame, (300, 300)),
#             1.0, (300, 300),
#             (104.0, 177.0, 123.0),
#             swapRB=False, crop=False
#         )
#         detector.setInput(imageBlob)
#         detections = detector.forward()

#         for i in range(0, detections.shape[2]):
#             confidence = detections[0, 0, i, 2]
#             if confidence <= conf:
#                 continue

#             box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#             (startX, startY, endX, endY) = box.astype("int")

#             # guard against out-of-bounds slices
#             startX = max(0, startX); startY = max(0, startY)
#             endX = min(w - 1, endX); endY = min(h - 1, endY)

#             face = frame[startY:endY, startX:endX]
#             if face.size == 0:
#                 continue
#             (fH, fW) = face.shape[:2]
#             if fW < 20 or fH < 20:
#                 continue

#             faceBlob = cv2.dnn.blobFromImage(
#                 face, 1.0/255, (96, 96), (0, 0, 0),
#                 swapRB=True, crop=False
#             )
#             embedder.setInput(faceBlob)
#             vec = embedder.forward()

#             preds = recognizer.predict_proba(vec)[0]
#             j = np.argmax(preds)
#             proba = preds[j]
#             name = le.classes_[j]

#             if proba >= 0.75:
#                 # If first time in this runtime loop, mark and send (subject to MessageLog)
#                 if name not in marked_students:
#                     # Mark attendance inside app context
#                     with app.app_context():
#                         mark_attendance(name)

#                         # WhatsApp send logic limited to morning/afternoon
#                         today_str = datetime.now().strftime("%Y-%m-%d")
#                         period = get_period()

#                         # check MessageLog (must be within app context)
#                         already_sent = MessageLog.query.filter_by(
#                             student_name=name,
#                             date=today_str,
#                             period=period
#                         ).first()

#                         if not already_sent:
#                             student = Student.query.filter_by(name=name).first()
#                             if student and getattr(student, "phone", None):
#                                 # Normalize phone: if no +, assume +91 if 10 digits
#                                 phone_raw = student.phone.strip()
#                                 if not phone_raw.startswith("+"):
#                                     # naive normalization: if 10 digits assume +91
#                                     digits = ''.join(ch for ch in phone_raw if ch.isdigit())
#                                     if len(digits) == 10:
#                                         phone_number = f"+91{digits}"
#                                     elif len(digits) > 10 and digits.startswith("91"):
#                                         phone_number = f"+{digits}"
#                                     else:
#                                         phone_number = phone_raw  # fallback
#                                 else:
#                                     phone_number = phone_raw

#                                 msg = f"Hello {name}, your attendance is marked at {datetime.now().strftime('%H:%M:%S')}."
#                                 try:
#                                     send_whatsapp_message(phone_number, msg)
#                                     print(f"WhatsApp sent to {name} ({phone_number}) for {period}")
#                                 except Exception as e:
#                                     print("Error sending WhatsApp:", e)

#                                 # log the message so it won't be sent again for this period
#                                 log = MessageLog(student_name=name, date=today_str, period=period)
#                                 db.session.add(log)
#                                 db.session.commit()
#                             else:
#                                 print(f"No phone for {name} — skipping WhatsApp")
#                         else:
#                             print(f"Already sent WhatsApp to {name} in {period}")

#                     marked_students.add(name)
#                     # UI message handling
#                     if message_state.get(name) != "marked":
#                         text = "{} : {:.2f}%".format(name, proba * 100)
#                         message = f"Attendance marked for {name}"
#                         message_display_time = time.time()
#                         message_state[name] = "marked"
#                     else:
#                         text = ""
#                 else:
#                     # already seen in this runtime loop
#                     if message_state.get(name) != "already":
#                         text = "{} : {:.2f}%".format(name, proba * 100)
#                         message = f"Attendance already marked for {name}"
#                         message_display_time = time.time()
#                         message_state[name] = "already"
#                     else:
#                         text = ""
#             else:
#                 text = "Unknown"

#             y = startY - 10 if startY - 10 > 10 else startY + 10
#             cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
#             cv2.putText(frame, text, (startX, y),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#         if message and time.time() - message_display_time < 3:
#             cv2.putText(frame, message, (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
#         else:
#             message = ""

#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame_bytes = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

#     cam.release()

# # -------------------------------
# # Routes
# # -------------------------------
# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/attendance')
# def show_attendance():
#     data = Attendance.query.order_by(Attendance.id.desc()).all()
#     return render_template('attendance.html', data=data)

# @app.route('/absent', methods=['GET'])
# def show_absent_page():
#     today = date.today()
#     today_str = today.strftime("%Y-%m-%d")

#     data = Attendance.query.filter(Attendance.date == today_str).all()
#     late_students = Attendance.query.filter(
#         Attendance.date == today_str,
#         Attendance.time > "09:15:00"
#     ).all()

#     all_students = Student.query.all()
#     all_names = {s.name for s in all_students}
#     present_names = {p.student_name for p in data}
#     absentees = sorted(all_names - present_names)

#     search_query = request.args.get('search', '').strip()
#     search_results = None

#     if search_query:
#         search_results = Attendance.query.filter(
#             or_(
#                 Attendance.student_name.ilike(f"%{search_query}%"),
#                 Attendance.status.ilike(f"%{search_query}%"),
#                 cast(Attendance.date, String).ilike(f"%{search_query}%"),
#                 cast(Attendance.time, String).ilike(f"%{search_query}%")
#             )
#         ).all()
#         absentees_filtered = [s for s in absentees if search_query.lower() in s.lower()]
#     else:
#         absentees_filtered = absentees

#     return render_template(
#         "absent.html",
#         data=data,
#         late_students=late_students,
#         absentees=absentees_filtered,
#         current_date=today_str,
#         search_query=search_query,
#         search_results=search_results
#     )

# @app.route('/admin_login', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
#             session['admin'] = True
#             return redirect(url_for('show_absent_page'))

#         return render_template('admin_login.html', error="Invalid credentials!")

#     return render_template('admin_login.html')

# @app.route('/admin_logout')
# def admin_logout():
#     session.pop('admin', None)
#     return redirect(url_for('show_attendance'))

# @app.route('/add', methods=['POST'])
# def add_student():
#     data = request.get_json()
#     # Accept phone if provided
#     new_student = Student(name=data['name'], rollno=data['rollno'], phone=data.get('phone'))
#     db.session.add(new_student)
#     db.session.commit()
#     return jsonify({'message': 'Student added successfully'})

# @app.route('/students', methods=['GET'])
# def get_students():
#     students = Student.query.all()
#     result = [{'id': s.id, 'name': s.name, 'rollno': s.rollno, 'phone': s.phone} for s in students]
#     return jsonify(result)

# @app.route('/update/<int:id>', methods=['PUT'])
# def update_student(id):
#     student = Student.query.get(id)
#     if not student:
#         return jsonify({'message': 'Student not found'})
#     data = request.get_json()
#     student.name = data.get('name', student.name)
#     student.rollno = data.get('rollno', student.rollno)
#     student.phone = data.get('phone', student.phone)
#     db.session.commit()
#     return jsonify({'message': 'Student updated successfully'})

# @app.route('/delete_attendance/<int:id>', methods=['POST'])
# def delete_attendance(id):
#     record = Attendance.query.get(id)
#     if record:
#         db.session.delete(record)
#         db.session.commit()
#     return redirect(url_for('show_attendance'))

# if __name__ == "__main__":
#     app.run(debug=True)




#voice assists 

# from flask import Flask, render_template, Response, redirect, session, send_file, request, url_for, jsonify
# import numpy as np
# import imutils
# import pickle
# import cv2
# import time
# from datetime import datetime, date
# import json
# import os
# import csv
# import io
# import requests
# import threading
# import re

# from gtts import gTTS
# from playsound import playsound

# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import or_, cast, String

# # ---------------------------
# # CONFIG
# # ---------------------------
# app = Flask(__name__)
# app.secret_key = "mysecretkey123"

# # ---------------------------
# # ULTRAMSG WHATSAPP CONFIG
# # ---------------------------
# ULTRA_INSTANCE_ID = "instance150419"
# ULTRA_TOKEN = "ffm5tlm6x0gqp4ue"

# def send_whatsapp_message(phone_number, message_text):
#     url = f"https://api.ultramsg.com/{ULTRA_INSTANCE_ID}/messages/chat"
#     data = {
#         "token": ULTRA_TOKEN,
#         "to": phone_number,
#         "body": message_text
#     }
#     try:
#         response = requests.post(url, data=data, timeout=10)
#         print("WhatsApp Response:", response.text)
#     except Exception as e:
#         print("WhatsApp send error:", e)

# # ---------------------------
# # SOUNDS (GTTS + playsound)
# # ---------------------------
# SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")
# os.makedirs(SOUNDS_DIR, exist_ok=True)

# def _safe_filename(s: str) -> str:
#     # remove unsafe chars
#     s = s.strip().lower()
#     s = re.sub(r'\s+', '_', s)
#     s = re.sub(r'[^a-z0-9_\-]', '', s)
#     return s[:100]

# def _voice_filename(kind: str, name: str) -> str:
#     # kind: "marked" or "already"
#     safe_name = _safe_filename(name)
#     return os.path.join(SOUNDS_DIR, f"{kind}_{safe_name}.mp3")

# def _generate_voice_file_if_missing(kind: str, name: str, text: str):
#     """Generate MP3 via gTTS if not already present."""
#     path = _voice_filename(kind, name)
#     if os.path.exists(path):
#         return path
#     try:
#         tts = gTTS(text=text, lang="en", slow=False)
#         tts.save(path)
#         print(f"Generated TTS file: {path}")
#         return path
#     except Exception as e:
#         print("gTTS generation error:", e)
#         return None

# def _play_file(path):
#     try:
#         if path and os.path.exists(path):
#             playsound(path)
#         else:
#             print("[Audio] file missing:", path)
#     except Exception as e:
#         print("playsound error:", e)

# def play_voice_async(kind: str, name: str, text_template: str):
#     """Create (if needed) and play the voice in a background thread."""
#     def worker():
#         try:
#             text = text_template.replace("{name}", name)
#             path = _generate_voice_file_if_missing(kind, name, text)
#             if path:
#                 _play_file(path)
#         except Exception as e:
#             print("Voice worker error:", e)
#     t = threading.Thread(target=worker, daemon=True)
#     t.start()

# # ---------------------------
# # DATABASE CONFIG
# # ---------------------------
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0606@localhost:5433/attendance_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # --------- Tables ---------
# class Student(db.Model):
#     __tablename__ = 'students'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50))
#     rollno = db.Column(db.Integer)
#     phone = db.Column(db.String(20))

# class Attendance(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_name = db.Column(db.String(50), nullable=False)
#     status = db.Column(db.String(20), nullable=False, default="Present")
#     date = db.Column(db.String(20), nullable=False)
#     time = db.Column(db.String(20), nullable=False)

# class MessageLog(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_name = db.Column(db.String(50))
#     date = db.Column(db.String(20))
#     period = db.Column(db.String(20))

# with app.app_context():
#     db.create_all()

# # ---------------------------
# # LOAD MODELS
# # ---------------------------
# embeddingModel = "model/openface_nn4.small2.v1.t7"
# recognizerFile = "output/recognizer.pickle"
# labelEncFile = "output/le.pickle"
# conf = 0.5

# print("Loading models...")
# prototxt = "model/deploy.prototxt"
# model = "model/res10_300x300_ssd_iter_140000.caffemodel"

# detector = cv2.dnn.readNetFromCaffe(prototxt, model)
# embedder = cv2.dnn.readNetFromTorch(embeddingModel)
# recognizer = pickle.loads(open(recognizerFile, "rb").read())
# le = pickle.loads(open(labelEncFile, "rb").read())

# message = ""
# attendance = {}
# ADMIN_USERNAME = "Admin"
# ADMIN_PASSWORD = "Admin"

# # ---------------------------
# # Helpers
# # ---------------------------
# def get_period():
#     hour = datetime.now().hour
#     return "morning" if hour < 12 else "afternoon"

# def mark_attendance(name):
#     date_str = datetime.now().strftime("%Y-%m-%d")
#     time_str = datetime.now().strftime("%H:%M:%S")

#     with app.app_context():
#         existing = Attendance.query.filter_by(student_name=name, date=date_str).first()
#         if not existing:
#             entry = Attendance(student_name=name, date=date_str, time=time_str, status="Present")
#             db.session.add(entry)
#             db.session.commit()
#             print(f"Attendance marked for {name}")
#             return True
#         return False

# # Voice message templates (you asked: include person name)
# VOICE_MARKED_TEMPLATE = "Attendance marked {name}"
# VOICE_ALREADY_TEMPLATE = "Attendance already marked {name}"

# # ---------------------------
# # Camera / Recognition Loop
# # ---------------------------
# def generate_frames():
#     global message
#     cam = cv2.VideoCapture(0)
#     time.sleep(2.0)

#     message_display_time = 0
#     marked_students = set()
#     message_state = {}

#     while True:
#         success, frame = cam.read()
#         if not success:
#             break

#         frame = imutils.resize(frame, width=600)
#         (h, w) = frame.shape[:2]

#         imageBlob = cv2.dnn.blobFromImage(
#             cv2.resize(frame, (300, 300)),
#             1.0, (300, 300),
#             (104.0, 177.0, 123.0),
#             swapRB=False, crop=False
#         )
#         detector.setInput(imageBlob)
#         detections = detector.forward()

#         for i in range(detections.shape[2]):
#             confidence = detections[0, 0, i, 2]
#             if confidence <= conf:
#                 continue

#             box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#             (startX, startY, endX, endY) = box.astype("int")

#             # bounds guard
#             startX = max(0, startX); startY = max(0, startY)
#             endX = min(w - 1, endX); endY = min(h - 1, endY)

#             face = frame[startY:endY, startX:endX]
#             if face.size == 0:
#                 continue
#             (fH, fW) = face.shape[:2]
#             if fW < 20 or fH < 20:
#                 continue

#             faceBlob = cv2.dnn.blobFromImage(
#                 face, 1.0/255, (96, 96), (0, 0, 0),
#                 swapRB=True, crop=False
#             )
#             embedder.setInput(faceBlob)
#             vec = embedder.forward()

#             preds = recognizer.predict_proba(vec)[0]
#             j = np.argmax(preds)
#             proba = preds[j]
#             name = le.classes_[j]

#             if proba >= 0.75:
#                 # first time seen during this runtime loop
#                 if name not in marked_students:
#                     # mark attendance and send whatsapp (inside app context)
#                     with app.app_context():
#                         mark_attendance(name)

#                         today_str = datetime.now().strftime("%Y-%m-%d")
#                         period = get_period()

#                         already_sent = MessageLog.query.filter_by(
#                             student_name=name,
#                             date=today_str,
#                             period=period
#                         ).first()

#                         if not already_sent:
#                             student = Student.query.filter_by(name=name).first()
#                             if student and getattr(student, "phone", None):
#                                 # normalize phone
#                                 phone_raw = student.phone.strip()
#                                 if not phone_raw.startswith("+"):
#                                     digits = ''.join(ch for ch in phone_raw if ch.isdigit())
#                                     phone_number = f"+91{digits}" if len(digits) == 10 else phone_raw
#                                 else:
#                                     phone_number = phone_raw

#                                 msg = f"Hello {name}, your attendance is marked at {datetime.now().strftime('%H:%M:%S')}."
#                                 send_whatsapp_message(phone_number, msg)

#                                 log = MessageLog(student_name=name, date=today_str, period=period)
#                                 db.session.add(log)
#                                 db.session.commit()

#                     # mark in runtime set
#                     marked_students.add(name)

#                     # UI message
#                     message = f"Attendance marked successfully for {name}"
#                     text = f"{name}: {proba*100:.2f}%"
#                     message_display_time = time.time()

#                     # play voice (asynchronously) — includes name
#                     play_voice_async("marked", name, VOICE_MARKED_TEMPLATE)

#                 else:
#                     # already marked (same day)
#                     message = f"Attendance already marked for {name}"
#                     text = f"{name}: {proba*100:.2f}%"
#                     message_display_time = time.time()

#                     # play voice for already (asynchronously)
#                     play_voice_async("already", name, VOICE_ALREADY_TEMPLATE)
#             else:
#                 text = "Unknown"

#             y = startY - 10 if startY - 10 > 10 else startY + 10
#             cv2.rectangle(frame, (startX, startY), (endX, endY), (0,255,0), 2)
#             cv2.putText(frame, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

#         # display a short message for 3 seconds
#         if message and time.time() - message_display_time < 3:
#             cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
#         else:
#             message = ""

#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame_bytes = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

#     cam.release()

# # ---------------------------
# # Routes
# # ---------------------------
# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/attendance')
# def show_attendance():
#     data = Attendance.query.order_by(Attendance.id.desc()).all()
#     return render_template('attendance.html', data=data)

# @app.route('/absent', methods=['GET'])
# def show_absent_page():
#     today = date.today()
#     today_str = today.strftime("%Y-%m-%d")

#     data = Attendance.query.filter(Attendance.date == today_str).all()
#     late_students = Attendance.query.filter(
#         Attendance.date == today_str,
#         Attendance.time > "09:15:00"
#     ).all()

#     all_students = Student.query.all()
#     all_names = {s.name for s in all_students}
#     present_names = {p.student_name for p in data}
#     absentees = sorted(all_names - present_names)

#     search_query = request.args.get('search', '').strip()
#     search_results = None

#     if search_query:
#         search_results = Attendance.query.filter(
#             or_(
#                 Attendance.student_name.ilike(f"%{search_query}%"),
#                 Attendance.status.ilike(f"%{search_query}%"),
#                 cast(Attendance.date, String).ilike(f"%{search_query}%"),
#                 cast(Attendance.time, String).ilike(f"%{search_query}%")
#             )
#         ).all()

#         absentees_filtered = [s for s in absentees if search_query.lower() in s.lower()]
#     else:
#         absentees_filtered = absentees

#     return render_template(
#         "absent.html",
#         data=data,
#         late_students=late_students,
#         absentees=absentees_filtered,
#         current_date=today_str,
#         search_query=search_query,
#         search_results=search_results
#     )

# @app.route('/admin_login', methods=['GET', 'POST'])
# def admin_login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
#             session['admin'] = True
#             return redirect(url_for('show_absent_page'))

#         return render_template('admin_login.html', error="Invalid credentials!")

#     return render_template('admin_login.html')

# @app.route('/admin_logout')
# def admin_logout():
#     session.pop('admin', None)
#     return redirect(url_for('show_attendance'))

# @app.route('/add', methods=['POST'])
# def add_student():
#     data = request.get_json()
#     new_student = Student(name=data['name'], rollno=data['rollno'], phone=data.get('phone'))
#     db.session.add(new_student)
#     db.session.commit()
#     return jsonify({'message': 'Student added successfully'})

# @app.route('/students', methods=['GET'])
# def get_students():
#     students = Student.query.all()
#     result = [{'id': s.id, 'name': s.name, 'rollno': s.rollno, 'phone': s.phone} for s in students]
#     return jsonify(result)

# @app.route('/update/<int:id>', methods=['PUT'])
# def update_student(id):
#     student = Student.query.get(id)
#     if not student:
#         return jsonify({'message': 'Student not found'})
#     data = request.get_json()
#     student.name = data.get('name', student.name)
#     student.rollno = data.get('rollno', student.rollno)
#     student.phone = data.get('phone', student.phone)
#     db.session.commit()
#     return jsonify({'message': 'Student updated successfully'})

# @app.route('/delete_attendance/<int:id>', methods=['POST'])
# def delete_attendance(id):
#     record = Attendance.query.get(id)
#     if record:
#         db.session.delete(record)
#         db.session.commit()
#     return redirect(url_for('show_attendance'))

# if __name__ == "__main__":
#     app.run(debug=True)




from flask import Flask, render_template, Response, redirect, session, send_file, request, url_for, jsonify
import numpy as np
import imutils
import pickle
import cv2
import time
from datetime import datetime, date
import json
import os
import csv
import io
import requests
import threading
import re

from gtts import gTTS
from playsound import playsound

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, cast, String

# ---------------------------
# CONFIG
# ---------------------------
app = Flask(__name__)
app.secret_key = "mysecretkey123"

# ---------------------------
# ULTRAMSG WHATSAPP CONFIG
# ---------------------------
ULTRA_INSTANCE_ID = "instance150419"
ULTRA_TOKEN = "ffm5tlm6x0gqp4ue"

def send_whatsapp_message(phone_number, message_text):
    url = f"https://api.ultramsg.com/{ULTRA_INSTANCE_ID}/messages/chat"
    data = {
        "token": ULTRA_TOKEN,
        "to": phone_number,
        "body": message_text
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        print("WhatsApp Response:", response.text)
    except Exception as e:
        print("WhatsApp send error:", e)

# ---------------------------
# SOUNDS (GTTS + playsound)
# ---------------------------
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")
os.makedirs(SOUNDS_DIR, exist_ok=True)

def _safe_filename(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'[^a-z0-9_\-]', '', s)
    return s[:100]

def _voice_filename(kind: str, name: str) -> str:
    safe_name = _safe_filename(name)
    return os.path.join(SOUNDS_DIR, f"{kind}_{safe_name}.mp3")

def _generate_voice_file_if_missing(kind: str, name: str, text: str):
    path = _voice_filename(kind, name)
    if os.path.exists(path):
        return path
    try:
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(path)
        print(f"Generated TTS file: {path}")
        return path
    except Exception as e:
        print("gTTS generation error:", e)
        return None

def _play_file(path):
    try:
        if path and os.path.exists(path):
            playsound(path)
        else:
            print("[Audio] file missing:", path)
    except Exception as e:
        print("playsound error:", e)

def play_voice_async(kind: str, name: str, text_template: str):
    """Create (if needed) and play the voice in a background thread."""
    def worker():
        try:
            text = text_template.replace("{name}", name)
            path = _generate_voice_file_if_missing(kind, name, text)
            if path:
                _play_file(path)
        except Exception as e:
            print("Voice worker error:", e)
    threading.Thread(target=worker, daemon=True).start()

# ---------------------------
# DATABASE CONFIG
# ---------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0606@localhost:5433/attendance_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --------- TABLES ---------
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    rollno = db.Column(db.Integer)
    phone = db.Column(db.String(20))


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Present")
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)


# MessageLog includes "type" (whatsapp / voice)
class MessageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(50))
    date = db.Column(db.String(20))
    period = db.Column(db.String(20))      # morning / afternoon
    type = db.Column(db.String(20))        # whatsapp / voice

with app.app_context():
    db.create_all()

    # Automatic safe migration: add message_log.type if missing
    try:
        col_check = db.session.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='message_log' AND column_name='type';
        """).fetchone()
        if not col_check:
            db.session.execute("""
                ALTER TABLE message_log ADD COLUMN type VARCHAR(20);
            """)
            db.session.commit()
            print("✔ message_log.type column added automatically")
    except Exception as e:
        # If any error occurs, print and continue (table may not exist yet, or permissions)
        print("Migration check/alter error:", e)

# ---------------------------
# LOAD MODELS
# ---------------------------
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

message = ""
ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "Admin"

# Voice templates including person name
VOICE_MARKED_TEMPLATE = "Attendance marked {name}"
VOICE_ALREADY_TEMPLATE = "Attendance already marked {name}"

# ---------------------------
# HELPERS
# ---------------------------
def get_period():
    hour = datetime.now().hour
    return "morning" if hour < 12 else "afternoon"

def mark_attendance(name):
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M:%S")

    with app.app_context():
        existing = Attendance.query.filter_by(student_name=name, date=date_str).first()
        if not existing:
            entry = Attendance(
                student_name=name,
                date=date_str,
                time=time_str,
                status="Present"
            )
            db.session.add(entry)
            db.session.commit()
            print(f"Attendance marked for {name}")
            return True
        return False

# ---------------------------
# CAMERA / FACE RECOGNITION
# ---------------------------
def generate_frames():
    global message
    cam = cv2.VideoCapture(0)
    time.sleep(2.0)

    message_display_time = 0
    marked_students = set()
    message_state = {}

    while True:
        success, frame = cam.read()
        if not success:
            break

        frame = imutils.resize(frame, width=600)
        (h, w) = frame.shape[:2]

        imageBlob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            1.0, (300, 300),
            (104.0, 177.0, 123.0),
            swapRB=False, crop=False
        )

        detector.setInput(imageBlob)
        detections = detector.forward()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence <= conf:
                continue

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            startX = max(0, startX)
            startY = max(0, startY)
            endX = min(w - 1, endX)
            endY = min(h - 1, endY)

            face = frame[startY:endY, startX:endX]
            if face.size == 0:
                continue
            (fH, fW) = face.shape[:2]
            if fW < 20 or fH < 20:
                continue

            faceBlob = cv2.dnn.blobFromImage(
                face, 1.0/255, (96,96), (0,0,0),
                swapRB=True, crop=False
            )
            embedder.setInput(faceBlob)
            vec = embedder.forward()

            preds = recognizer.predict_proba(vec)[0]
            j = np.argmax(preds)
            proba = preds[j]
            name = le.classes_[j]

            if proba >= 0.75:

                # ------------------------------
                # FIRST TIME IN THIS CAMERA RUN
                # ------------------------------
                if name not in marked_students:

                    # ------------ Attendance + WhatsApp ----------
                    with app.app_context():
                        mark_attendance(name)

                        today_str = datetime.now().strftime("%Y-%m-%d")
                        period = get_period()

                        sent_log = MessageLog.query.filter_by(
                            student_name=name,
                            date=today_str,
                            period=period,
                            type="whatsapp"
                        ).first()

                        if not sent_log:
                            student = Student.query.filter_by(name=name).first()
                            if student and student.phone:
                                raw = student.phone.strip()
                                if not raw.startswith("+"):
                                    digits = ''.join(ch for ch in raw if ch.isdigit())
                                    if len(digits) == 10:
                                        phone = f"+91{digits}"
                                    else:
                                        phone = raw
                                else:
                                    phone = raw

                                msg = f"Hello {name}, your attendance is marked at {datetime.now().strftime('%H:%M:%S')}."
                                send_whatsapp_message(phone, msg)

                                log = MessageLog(
                                    student_name=name,
                                    date=today_str,
                                    period=period,
                                    type="whatsapp"
                                )
                                db.session.add(log)
                                db.session.commit()

                        # ------------------------------
                        # VOICE LIMIT (Morning + Afternoon)
                        # ------------------------------
                        voice_log = MessageLog.query.filter_by(
                            student_name=name,
                            date=today_str,
                            period=period,
                            type="voice"
                        ).first()

                        if not voice_log:
                            # play marked voice only ONCE per period
                            play_voice_async("marked", name, VOICE_MARKED_TEMPLATE)

                            v = MessageLog(
                                student_name=name,
                                date=today_str,
                                period=period,
                                type="voice"
                            )
                            db.session.add(v)
                            db.session.commit()
                        else:
                            print(f"Voice already played for {name} in {period}")

                    # update runtime
                    marked_students.add(name)

                    message = f"Attendance marked {name}"
                    text = f"{name}: {proba*100:.2f}%"
                    message_display_time = time.time()

                else:
                    # ------------------------------
                    # ALREADY MARKED TODAY
                    # ------------------------------
                    message = f"Attendance already marked {name}"
                    text = f"{name}: {proba*100:.2f}%"
                    message_display_time = time.time()

                    # voice only if allowed (per period)
                    with app.app_context():
                        today_str = datetime.now().strftime("%Y-%m-%d")
                        period = get_period()

                        voice_log = MessageLog.query.filter_by(
                            student_name=name,
                            date=today_str,
                            period=period,
                            type="voice"
                        ).first()

                        if not voice_log:
                            play_voice_async("already", name, VOICE_ALREADY_TEMPLATE)

                            v = MessageLog(
                                student_name=name,
                                date=today_str,
                                period=period,
                                type="voice"
                            )
                            db.session.add(v)
                            db.session.commit()

            else:
                text = "Unknown"

            # Draw boxes & text
            y = startY - 10 if startY - 10 > 10 else startY + 10
            cv2.rectangle(frame, (startX,startY), (endX,endY), (0,255,0),2)
            cv2.putText(frame, text, (startX,y),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)

        # message for 3 seconds
        if message and time.time() - message_display_time < 3:
            cv2.putText(frame, message, (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
        else:
            message = ""

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

    cam.release()

# ---------------------------
# ROUTES
# ---------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance')
def show_attendance():
    data = Attendance.query.order_by(Attendance.id.desc()).all()
    return render_template('attendance.html', data=data)

@app.route('/absent', methods=['GET'])
def show_absent_page():
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    data = Attendance.query.filter(Attendance.date == today_str).all()
    late_students = Attendance.query.filter(
        Attendance.date == today_str,
        Attendance.time > "09:15:00"
    ).all()

    all_students = Student.query.all()
    all_names = {s.name for s in all_students}
    present_names = {p.student_name for p in data}

    absentees = sorted(all_names - present_names)

    search_query = request.args.get('search', '').strip()
    search_results = None

    if search_query:
        search_results = Attendance.query.filter(
            or_(
                Attendance.student_name.ilike(f"%{search_query}%"),
                Attendance.status.ilike(f"%{search_query}%"),
                cast(Attendance.date, String).ilike(f"%{search_query}%"),
                cast(Attendance.time, String).ilike(f"%{search_query}%")
            )
        ).all()
        absentees_filtered = [s for s in absentees if search_query.lower() in s.lower()]
    else:
        absentees_filtered = absentees

    return render_template("absent.html",
                           data=data,
                           late_students=late_students,
                           absentees=absentees_filtered,
                           current_date=today_str,
                           search_query=search_query,
                           search_results=search_results)

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("show_absent_page"))
        else:
            return render_template("admin_login.html",
                                   error="Invalid credentials!")

    return render_template("admin_login.html")

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('show_attendance'))

@app.route('/add', methods=['POST'])
def add_student():
    data = request.get_json()
    new_student = Student(
        name=data["name"],
        rollno=data["rollno"],
        phone=data.get("phone")
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"message": "Student added successfully"})

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    result = [
        {"id": s.id, "name": s.name, "rollno": s.rollno, "phone": s.phone}
        for s in students
    ]
    return jsonify(result)

@app.route('/update/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({"message": "Student not found"})

    data = request.get_json()
    student.name = data.get("name", student.name)
    student.rollno = data.get("rollno", student.rollno)
    student.phone = data.get("phone", student.phone)
    db.session.commit()

    return jsonify({"message": "Student updated successfully"})

@app.route('/delete_attendance/<int:id>', methods=['POST'])
def delete_attendance(id):
    record = Attendance.query.get(id)
    if record:
        db.session.delete(record)
        db.session.commit()
    return redirect(url_for("show_attendance"))

if __name__ == "__main__":
    app.run(debug=True)
