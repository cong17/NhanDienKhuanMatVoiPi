

from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
from threading import Thread
import os
import sqlite3


# Ham phat ra am thanh
def play_sound(path):
    os.system("mpg123 " + path)


# Hàm lấy thông tin người dùng qua ID
def getProfile(id):
    conn = sqlite3.connect("dbNhanDien.db")
    cursor = conn.execute("SELECT name,address FROM info WHERE ID=" + str(id))
    profile = None
    for row in cursor:
        profile = row
        profile = str(profile).replace("'", "")
    conn.close()
    return profile


data = pickle.loads(open("encodings", "rb").read())
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# khởi tạo luồng video và bật camera lên
print("Bắt đầu đọc cammera")
vs = VideoStream(src=0).start()

time.sleep(2.0)

t = Thread(target=play_sound, args=("sounds/ready.mp3", ))
t.deamon = True
t.start()

time.sleep(2.0)

i_frame = 0
while True:
    # Doc tung frame
    frame = vs.read()
    frame = imutils.resize(frame, width=320)
    i_frame += 1

    # Xu ly detection moi 20 frame de giam tai cho Pi
    if i_frame % 1200 == 0:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # phat hien khuan mat
        rects = detector.detectMultiScale(gray,
                                          scaleFactor=1.1,
                                          minNeighbors=5,
                                          minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)
        count_n = len(rects)
        if count_n == 1:
            # OpenCV trả về tọa độ hộp giới hạn theo thứ tự (x, y, w, h) xap xep theo thu tu chieu kim dong ho
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

            # tinh toan dac trung tung khuan mat phat hien duoc
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []#chua ten nguoi nhan ra

            # lap cac khuan mat
            for encoding in encodings:
                # so sanh voi file ma train ra

                matches = face_recognition.compare_faces(data["encodings"],
                                                         encoding,
                                                         tolerance=0.4)
                name = "999"

                # kiem tra xem co trung voi khuan mat nao khong
                if True in matches:
                    
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # determine the recognized face with the largest number
                    # of votes (note: in the event of an unlikely tie Python
                    # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)

                # chen ten vao
                names.append(name)

            # loop over the recognized faces
            for ((top, right, bottom, left), name) in zip(boxes, names):
                #ve o vuong xung quanh mat
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0),
                              2)
                y = top - 15 if top - 15 > 15 else top + 15
                info = getProfile(name)

                cv2.putText(frame, str(info), (left - 10, top),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                #phat am thanh
                if name != 999:
                    pathMusix = "sounds/id-" + name + ".mp3"
                    t = Thread(target=play_sound, args=(pathMusix, ))
                    t.deamon = True
                    t.start()
                    time.sleep(2.0)
        elif count_n > 1:
            pathMusix = "sounds/sn-" + str(count_n) + ".mp3"
            t = Thread(target=play_sound, args=(pathMusix, ))
            t.deamon = True
            t.start()
            time.sleep(2.0)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

cv2.destroyAllWindows()
vs.stop()
