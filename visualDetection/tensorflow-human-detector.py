# Code adapted from Tensorflow Object Detection Framework
# https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb
# Tensorflow Object Detection Detector

from pyimagesearch.centroidtracker import CentroidTracker
from facereq.recognize_faces_image import detectFaces
from imutils.video import VideoStream
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
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def processFrame(self, image):
        # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
        start_time = time.time()
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})
        end_time = time.time()

        print("Elapsed Time:", end_time-start_time)

        im_height, im_width,_ = image.shape
        boxes_list = [None for i in range(boxes.shape[1])]
        for i in range(boxes.shape[1]):
            boxes_list[i] = (int(boxes[0,i,1]*im_width), 
                        int(boxes[0,i,0] * im_height),
                        int(boxes[0,i,3]*im_width),
                        int(boxes[0,i,2] * im_height))

        return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

    def close(self):
        self.sess.close()
        self.default_graph.close()

def highlightObjectOnImage(img, name, center, boundaries):
    cv2.putText(img, name, (centroid[0] - 10, centroid[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.circle(img, (center[0], center[1]), 4, (0, 255, 0), -1)

    cv2.rectangle(img,(boundaries[0], boundaries[1]),(boundaries[2], boundaries[3]),(255,0,0),2)

def getHumanBoxes(boxes, scores, classes):
    humanBoxes = []
    for i in range(len(boxes)):
        if classes[i] == 1 and scores[i] > threshold:
            humanBoxes.append(boxes[i])
    
    return humanBoxes

if __name__ == "__main__":
    model_path = 'D:/Users/jose_/Desktop/Desarrollo/Human-Detector/ssdlite_mobilenet_v2_coco_2018_05_09/frozen_inference_graph.pb'
    pickle_path = "encodings.pickle"
    odapi = DetectorAPI(path_to_ckpt=model_path)
    tracker = CentroidTracker(1)
    threshold = 0.7
    cap = VideoStream(src=0).start()
    knownFaces = pickle.loads(open(pickle_path, "rb").read())

    recognized = {}

    while True:
        img = cap.read()
        img = cv2.resize(img, (1280, 720))
        displayImg = img.copy()

        boxes, scores, classes, num = odapi.processFrame(img)

        # Visualization of the results of a detection.
        objects, removed = tracker.update(getHumanBoxes(boxes, scores, classes))

        for k in removed:
            recognized.pop(k, None)

        for (objectID, (centroid, rect)) in objects.items():
            if (objectID not in recognized):
                subimg = img[rect[1]: rect[3], rect[0]: rect[2]]
                    
                try:
                    faces = detectFaces(subimg, knownFaces)
                    if len(faces) > 0:
                        recognized[objectID] = faces[0]
                except:
                    print("Not nice")
                    pass

                
            text = recognized[objectID] if (objectID in recognized) else "ID {}".format(objectID)
            highlightObjectOnImage(displayImg, text, centroid, rect)
            
        cv2.imshow("preview", displayImg)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break