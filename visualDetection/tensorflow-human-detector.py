# Code adapted from Tensorflow Object Detection Framework
# https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb
# Tensorflow Object Detection Detector

from pyimagesearch.centroidtracker import CentroidTracker
from facereq.recognize_faces_image import detectFaces
from imutils.video import VideoStream
from math_vec.utils import *
import numpy as np
import tensorflow as tf
import cv2
import time
import pickle


class DetectorAPI:
	def __init__(self, path_to_ckpt):
		self.path_to_ckpt = path_to_ckpt

		self.detection_graph = tf.Graph()
		with self.detection_graph.as_default():
			od_graph_def = tf.GraphDef()
			with tf.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
				serialized_graph = fid.read()
				od_graph_def.ParseFromString(serialized_graph)
				tf.import_graph_def(od_graph_def, name='')

		self.default_graph = self.detection_graph.as_default()
		self.sess = tf.Session(graph=self.detection_graph)

		# Definite input and output Tensors for detection_graph
		self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
		# Each box represents a part of the image where a particular object was detected.
		self.detection_boxes = self.detection_graph.get_tensor_by_name(
		    'detection_boxes:0')
		# Each score represent how level of confidence for each of the objects.
		# Score is shown on the result image, together with the class label.
		self.detection_scores = self.detection_graph.get_tensor_by_name(
		    'detection_scores:0')
		self.detection_classes = self.detection_graph.get_tensor_by_name(
		    'detection_classes:0')
		self.num_detections = self.detection_graph.get_tensor_by_name(
		    'num_detections:0')

	def processFrame(self, image):
		# Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
		image_np_expanded = np.expand_dims(image, axis=0)
		# Actual detection.
		start_time = time.time()
		(boxes, scores, classes, num) = self.sess.run(
			[self.detection_boxes, self.detection_scores,
			    self.detection_classes, self.num_detections],
			feed_dict={self.image_tensor: image_np_expanded})
		end_time = time.time()

		print("Elapsed Time:", end_time-start_time)

		im_height, im_width, _ = image.shape
		boxes_list = [None for i in range(boxes.shape[1])]
		for i in range(boxes.shape[1]):
			boxes_list[i] = (int(boxes[0, i, 1]*im_width),
						int(boxes[0, i, 0] * im_height),
						int(boxes[0, i, 3]*im_width),
						int(boxes[0, i, 2] * im_height))

		return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

	def close(self):
		self.sess.close()
		self.default_graph.close()


def highlightObjectOnImage(img, name, center, boundaries, color):
	cv2.putText(img, name, (centroid[0] - 10, centroid[1] - 10),
	            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
	cv2.circle(img, (center[0], center[1]), 4, (0, 255, 0), -1)
	cv2.rectangle(img, (boundaries[0], boundaries[1]),
	              (boundaries[2], boundaries[3]), color, 2)


def separateObjectsFromHuman(boxes, scores, classes):
    humanBoxes = []
    objectBoxes = []

    for i in range(len(boxes)):
        if scores[i] > threshold:
            if classes[i] == 1:
                humanBoxes.append(boxes[i])
            else:
                objectBoxes.append(boxes[i])

    return humanBoxes, objectBoxes


if __name__ == "__main__":
	model_path = 'D:/Users/jose_/Desktop/Desarrollo/TrackABull/visualDetection/faster_rcnn_inception_v2_coco_2018_01_28/frozen_inference_graph.pb'
	pickle_path = "encodings.pickle"
	odapi = DetectorAPI(path_to_ckpt=model_path)
	humanTracker = CentroidTracker(5)
	knownFaces = pickle.loads(open(pickle_path, "rb").read())
	objectTracker = CentroidTracker(5)
	qrDecoder = cv2.QRCodeDetector()
	cap = VideoStream(src=0).start()
	threshold = 0.8
	recognizedHumans = {}
	lastHumanPositions = {}
	recognizedObjects = {}
	lastObjectPositions = {}
	objectOwners = {}

	while True:
		img = cap.read()
		img = cv2.resize(img, (1280, 720))
		displayImg = img.copy()

		boxes, scores, classes, num = odapi.processFrame(img)

		humanBoxes, objectBoxes = separateObjectsFromHuman(
			boxes, scores, classes)
		# Visualization of the results of a detection.
		humans, removedHumans = humanTracker.update(humanBoxes)

		for k in removedHumans:
			recognizedHumans.pop(k, None)
			lastHumanPositions.pop(k, None)

		for (objectID, (centroid, rect)) in humans.items():
			if (objectID not in lastHumanPositions):
				lastHumanPositions[objectID] = [{"centroid": centroid, "rect": rect}]
			else:
				if (len(lastHumanPositions[objectID]) >= 4):
					lastHumanPositions[objectID].append({"centroid": centroid, "rect": rect})
					lastHumanPositions[objectID].pop(0)


			if (objectID not in recognizedHumans):
				subimg = img[rect[1]: rect[3], rect[0]: rect[2]]
					
				try:
					faces = detectFaces(subimg, knownFaces)
					if len(faces) > 0:
						recognizedHumans[objectID] = faces[0]
				except:
					print("Not nice")
					pass

				
			text = recognizedHumans[objectID] if (objectID in recognizedHumans) else "ID {}".format(objectID)
			highlightObjectOnImage(displayImg, text, centroid, rect, (255,0,0))

		objects, removedObjects = objectTracker.update(objectBoxes)

		for k in removedObjects:
			recognizedObjects.pop(k, None)
			lastObjectPositions.pop(k, None)

		for (objectID, (centroid, rect)) in objects.items():
			if (objectID not in lastObjectPositions):
				lastObjectPositions[objectID] = [{"centroid": centroid, "rect": rect}]
			else:
				if (len(lastObjectPositions[objectID]) >= 4):
					lastObjectPositions[objectID].append({"centroid": centroid, "rect": rect})
					lastObjectPositions[objectID].pop(0)
				

			# if (objectID not in recognizedObjects):
			subimg = img[rect[1]: rect[3], rect[0]: rect[2]]
			
			try:
				data,bbox,rectifiedImage = qrDecoder.detectAndDecode(subimg)
				if len(data) > 0:
					recognizedObjects[objectID] = data
			except:
				print("Not nice")
				pass

				
			text = ("thing " + recognizedObjects[objectID]) if (objectID in recognizedObjects) else "ID {}".format(objectID)
			highlightObjectOnImage(displayImg, text, centroid, rect, (0,0,255))
			
		for (objectID, name) in recognizedObjects.items():
			if (name not in objectOwners):
				objPos = lastObjectPositions[objectID]
				if (len(objPos) > 4):
					objPos0 = objPos[0]
					objPos1 = objPos[1]
					objPos2 = objPos[2]
					objPos3 = objPos[3]
					
					for (humanId, humanPositions) in lastHumanPositions:
						if (len(humanPositions) > 4):
							humanPos0 = humanPositions[0]
							humanPos1 = humanPositions[1]
							humanPos2 = humanPositions[2]
							humanPos3 = humanPositions[3]

							objRect3 = objPos3["rect"]
							humanRect3 = humanPos3["rect"]

							if (box_inside_box(objRect3[0], objRect3[1], objRect3[2], objRect3[3], humanRect3[0], humanRect3[1], humanRect3[2], humanRect3[3])):
								objCenter0 = objPos0["centroid"]
								humanCenter0 = humanPos0["centroid"]
								objCenter3 = objPos3["centroid"]
								humanCenter3 = humanPos3["centroid"]

								objVector = vector_change(objCenter0[0], objCenter0[1], objCenter3[0], objCenter3[1])
								humanVector = vector_change(humanCenter0[0], humanCenter0[1], humanCenter3[0], humanCenter3[1])

								sameX, samey = is_same_direction(objVector[0], objVector[1], humanVector[0], humanVector[1])

								if (sameX):
									objectOwners[name] = humanId
									print(recognizedHumans[humanId] + " took thing " + name)
									break
		
		cv2.imshow("preview", displayImg)
		key = cv2.waitKey(1)
		if key & 0xFF == ord('q'):
			break
