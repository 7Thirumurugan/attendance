# recognize_and_mark.py

import numpy as np
import cv2
import imutils
import pickle
import time
import csv
import datetime


# Load models
embeddingModel = "model/openface_nn4.small2.v1.t7"
recognizerFile = "output/recognizer.pickle"
labelEncFile = "output/le.pickle"
conf = 0.5

prototxt = "model/deploy.prototxt"
model = "model/res10_300x300_ssd_iter_140000.caffemodel"
detector = cv2.dnn.readNetFromCaffe(prototxt, model)
embedder = cv2.dnn.readNetFromTorch(embeddingModel)
recognizer = pickle.loads(open(recognizerFile, "rb").read())
le = pickle.loads(open(labelEncFile, "rb").read())


# Start webcam

cam = cv2.VideoCapture(0)
time.sleep(2.0)

marked_names = set()

while True:
    ret, frame = cam.read()
    if not ret:
        break

    frame = imutils.resize(frame, width=600)
    (h, w) = frame.shape[:2]

    imageBlob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                      (300, 300), (104.0, 177.0, 123.0),
                                      swapRB=False, crop=False)
    detector.setInput(imageBlob)
    detections = detector.forward()


    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            face = frame[startY:endY, startX:endX]
            (fH, fW) = face.shape[:2]

            if fW < 20 or fH < 20:
                continue

            faceBlob = cv2.dnn.blobFromImage(face, 1.0/255, (96, 96), (0,0,0),
                                             swapRB=True, crop=False)
            embedder.setInput(faceBlob)
            vec = embedder.forward()

            preds = recognizer.predict_proba(vec)[0]
            j = np.argmax(preds)
            proba = preds[j]
            name = le.classes_[j]

            if proba > 0.5 and name not in marked_names:
                now = datetime.datetime.now()
                timestamp = now.strftime("%H:%M:%S")
                with open("attendance.csv", "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([name, timestamp])
                marked_names.add(name)
                print(f"Marked {name} at {timestamp}")

    # Break condition if needed
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # Press Esc to stop
        break

cam.release()
cv2.destroyAllWindows()
