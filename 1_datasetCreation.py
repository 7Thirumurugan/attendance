
import imutils
import time
import cv2
import csv
import os

#cascade = 'haarcascade_frontalface_default.xml'
cascade = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
detector = cv2.CascadeClassifier(cascade)

Name = str(input("Enter your Name : "))
Roll_Number = int(input("Enter your Roll_Number : "))
dataset = 'dataset'
sub_data = Name
path = os.path.join(dataset, sub_data)

if not os.path.isdir(path):
    os.mkdir(path)
    print(sub_data)

info = [str(Name), str(Roll_Number)]
with open('student.csv', 'a') as csvFile:
    write = csv.writer(csvFile)
    write.writerow(info)
csvFile.close()


print("Starting video stream...")
cam = cv2.VideoCapture(0)
time.sleep(8.0)
total = 0

while total < 25:
    print(total)
    _, frame = cam.read()
    img = imutils.resize(frame, width=400)
    rects = detector.detectMultiScale(
        cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), scaleFactor=1.1,
        minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in rects:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        p = os.path.sep.join([path, "{}.png".format(
            str(total).zfill(5))])
        cv2.imwrite(p, img)
        total += 1

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break



cam.release()
cv2.destroyAllWindows()



'''
import imutils
import time
import cv2
import csv
import os

# Load face cascade
cascade = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
detector = cv2.CascadeClassifier(cascade)

# Input details
Name = str(input("Enter your Name : "))
Roll_Number = int(input("Enter your Roll_Number : "))
dataset = 'dataset'
sub_data = Name
path = os.path.join(dataset, sub_data)

if not os.path.isdir(path):
    os.mkdir(path)
    print("Folder created for:", sub_data)

# Save student info in CSV
info = [str(Name), str(Roll_Number)]
with open('student.csv', 'a', newline="") as csvFile:
    write = csv.writer(csvFile)
    write.writerow(info)

print("Loading image instead of video...")

# Load your image
image_path = "dataset/thiru.jpg"   # change with your uploaded image
frame = cv2.imread(image_path)

if frame is None:
    print("Error: Image not found!")
    exit()

frame = imutils.resize(frame, width=400)

# Detect faces
rects = detector.detectMultiScale(
    cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1,
    minNeighbors=5, minSize=(30, 30))

total = 0
for (x, y, w, h) in rects:
    # Crop face region
    face = frame[y:y+h, x:x+w]

    # Save the same face 10 times
    for i in range(10):
        p = os.path.sep.join([path, "{}.png".format(str(total).zfill(5))])
        cv2.imwrite(p, face)
        total += 1

    # Draw rectangle
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

cv2.imshow("Inserted Image", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(f"✅ {total} images saved in '{path}'")

'''