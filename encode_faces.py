
# import thu vien
from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os

# them agrument
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--detection-method", type=str, default="cnn",
	help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())

# Doc duong dan
print("[INFO] quantifying faces...")
imagePaths = list(paths.list_images("./dataset"))


knownEncodings = []
knownNames = []

#duyet anh
for (i, imagePath) in enumerate(imagePaths):

	print("[INFO] processing image {}/{}".format(i + 1,
		len(imagePaths)))
	name = imagePath.split(os.path.sep)[-2]

	
	image = cv2.imread(imagePath)
	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

	# phát hiện các phối hợp (x, y) của các hộp giới hạn
	# tương ứng với mỗi khuôn mặt trong hình ảnh đầu vào
	boxes = face_recognition.face_locations(rgb,
		model="hog")

	#tinh toan dac trung khuan mat
	encodings = face_recognition.face_encodings(rgb, boxes)

	
	for encoding in encodings:
		knownEncodings.append(encoding)
		knownNames.append(name)

#tao file chua cac dac trung khuan mat
print("[INFO] con meo ma treo...")
data = {"encodings": knownEncodings, "names": knownNames}
f = open("encodings", "wb")
f.write(pickle.dumps(data))
f.close()
