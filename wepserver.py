


#them cac thu vien
from imutils.video import VideoStream
# from flask import Response
# from flask import Flask
# from flask import render_template
from flask import *
import threading
import argparse
import datetime
import imutils
import time
import cv2
import face_recognition
import pickle
import os
import sqlite3
import numpy
from datetime import datetime


#doc file encoding va khoi tao trinh detect face
data = pickle.loads(open("encodings", "rb").read())
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


outputFrame = None
lock = threading.Lock()

app = Flask(__name__)


# Ham phat ra am thanh
def play_sound(path):
    os.system("mpg123 " + path)

# Hàm lấy thông tin người dùng qua ID
def getProfile(id):
    conn = sqlite3.connect("dbNhanDien.db")
    cursor = conn.execute("SELECT name,class FROM info WHERE ID=" + str(id))
    profile = None
    for row in cursor:
        profile = row
        profile = str(profile).replace("'", "")
    conn.close()
    return profile

def checkthongtin():
    conn = sqlite3.connect("dbNhanDien.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name,MSSV,Class,time from  info where id!=0")
    data = cursor.fetchall()
    # print(data)
    conn.close()
    return data

#hàm reset điểm danh
def resetCheckOut():
    conn = sqlite3.connect("dbNhanDien.db")
    cur = conn.cursor()

    cmd="UPDATE info SET Time = 0"
    conn.execute(cmd)
    conn.commit()
    conn.close()
    return 1

#hàm điểm danh
def checkOut(id):
    conn = sqlite3.connect("dbNhanDien.db")
    time=datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    cur = conn.cursor()
    cmd2="UPDATE info SET Time = '"+str(time)+"',checkout=1 where id="+str(id)
    conn.execute(cmd2)
    conn.commit()
    conn.close()
    return 1

#Hàm xử lý ảnh upload lên
#Nhận đầu vào là 1 ảnh và trả về thông tin người trong ảnh.
def detectPhoto(img):
    # img=cv2.imread(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    rects = detector.detectMultiScale(gray,scaleFactor=1.1,
                                          minNeighbors=5,
                                          minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)
    

    # OpenCV trả về tọa độ hộp giới hạn theo thứ tự (x, y, w, h) xap xep theo thu tu chieu kim dong ho
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    # tinh toan dac trung cua khuan mat phat hien ra
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []

    for encoding in encodings:
        # so sanh voi file ma train ra

        matches = face_recognition.compare_faces(data["encodings"],
                                                    encoding,
                                                    tolerance=0.4)
        name = "0"

        if True in matches:

            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            name = max(counts, key=counts.get)


        names.append(name)
        info = getProfile(name)
        return info

#controler trang chủ
@app.route("/")
def index():
    data=checkthongtin()
    return render_template("index.html",value=data)

def readFrame(frameCount):
    
    global vs, outputFrame, lock
    vs = VideoStream(src=0).start()
    time.sleep(2.0)


    while True:
        # time.sleep(1.0)
        frame = vs.read()
        frame = imutils.resize(frame, width=360)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Phat hien khuan mat
        rects = detector.detectMultiScale(gray,
                                          scaleFactor=1.1,
                                          minNeighbors=5,
                                          minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)
        count_n = len(rects)#so khuan mat phat hien

        if count_n == 1:
            # OpenCV trả về tọa độ hộp giới hạn theo thứ tự (x, y, w, h) xap xep theo thu tu chieu kim dong ho
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

            # tinh toan ra cac dac trung cua khuan mat phat hien ra
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

            for encoding in encodings:
                # so sanh voi file ma train ra

                matches = face_recognition.compare_faces(data["encodings"],
                                                         encoding,
                                                         tolerance=0.4)
                name = "999"

                if True in matches:
                    
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                 
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    name = max(counts, key=counts.get)

                # cap nhat ten vao danh sach 
                names.append(name)
                for ((top, right, bottom, left), name) in zip(boxes, names):
                    #ve o vuong xung quanh khuan mat
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0),
                                2)
                    y = top - 15 if top - 15 > 15 else top + 15

                    #viet thong tin len khuan mat va phat ra loa
                    if name != 999:
                        info = getProfile(name)
                        YesNo=checkOut(name)
                        print(info)
                        cv2.putText(frame, str(info), (left - 10, top),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                        # if YesNo==0:
                        #     cv2.putText(frame, "BAN DA DIEM DANH ROI!!!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        # elif YesNo==1:
                        pathMusix = "sounds/id-" + name + ".mp3"
                        t = threading.Thread(target=play_sound, args=(pathMusix, ))
                        t.deamon = True
                        t.start()
                        time.sleep(2.0)
                        
        elif count_n > 1:
            # pathMusix = "sounds/sn-" + str(count_n) + ".mp3"
            # t = threading.Thread(target=play_sound, args=(pathMusix, ))
            # t.deamon = True
            # t.start()
            # time.sleep(2.0)
            print(count_n)

                
     
        with lock:
            outputFrame = frame.copy()

#tao du lieu tra ve client   
def generate():
    global outputFrame, lock
    while True:

        with lock:

            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            if not flag:
                continue

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    t = threading.Thread(target=readFrame, args=(60,))
    t.daemon = True
    t.start()

    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

#reset col timeCheckout in db
@app.route('/rs', methods=['GET'])
def rs():
    if(resetCheckOut()):
        value="<h1> Sẵn sàng</h1>"
    return value


@app.route('/info', methods=['GET'])
def infoMember():
    return render_template("info.html")



@app.route('/uploaded', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        filestr = request.files['file'].read()
        npimg = numpy.fromstring(filestr, numpy.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        value=detectPhoto(img)
        return value


        

if __name__ == '__main__':


    #start Thong bao san san
    # pathMusix = "sounds/ready.mp3"
    # t = threading.Thread(target=play_sound, args=(pathMusix, ))
    # t.deamon = True
    # t.start()
    # time.sleep(2.0)

    # start the flask app
    # app.run()
    app.run(host= '0.0.0.0')

