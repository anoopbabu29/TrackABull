# Code adapted from Tensorflow Object Detection Framework
# https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb
# Tensorflow Object Detection Detector
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import os
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
    model_path = './ssdlite_mobilenet_v2_coco_2018_05_09/frozen_inference_graph.pb'
    pickle_path = "encodings.pickle"
    odapi = DetectorAPI(path_to_ckpt=model_path)
    tracker = CentroidTracker(1)
    threshold = 0.7
    cap = VideoStream(src=0).start()
    knownFaces = pickle.loads(open(pickle_path, "rb").read())

    recognized = {}

    credentials_dict = {
        "type": "service_account",
        "project_id": "trackabull",
        "private_key_id": "f57a28e8373ecce8522d0b8c08503577737fe594",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCM+Uwbf78W2FI9\ngS+XGjfUgpm6FdaJYeMBjS3glX5tGRffNHZCVlW0XtTaEfoIxRUXm3riFh1p2Li5\n61TEGEZhZJOVGOOLR4231WGcVw2RNZ9c3sOMtQLvob5/tSQ2C4JExzl5rP2Q7u9N\noBu3tDDLemRi1HG3Uhj7Zgvc5JFs12pBlAxDhfNNfJcmZhete/Hb7oHZbecJhcIz\n4XZAM7+n2DdWe4u46E258W7evK47VN3GxRdfQnR4mq6NO5qi7wsLIdsiUSwvWPl1\neU5UGMLWTrrZ+7dfvFFp79m+m4Z0OPc/Ue4xn9VHqIzf8fD+CWYTtColuOTHcTtI\n9f4mmDq1AgMBAAECggEAAZJnC5hzTkMnuZlW6UGo1TUGl0lWjM4bXKFRHWO1VuyU\ndE/usKMrTflPuMXCCrZ923dHmb1C4zMALkyGM7CMmlnnfl5abStlVGMr9TUQSOn2\n5q9yMT+0cm0UhXKE3phmwbMR/D4WTrcnUm+CV5xJ/f7Vnzd8tB1Ve3oiEDq5N2Q0\nRbhPey93ykZBBnqCWbyKgVSH82t5zlwepiuKBKbzeSqh7WwHAa/eLNIUXStgajER\nIbgGwApWMVWDwp38eIokHQa4o4wldmZ7KujM4a9jaW+0gDNGzuT9eCAGBO3iWy60\nz8Rv38HlxGxDTcxIdInjGtB4rJAAtnK+kCcRDjEO6QKBgQDAZMKRG/RLGCAkLeyb\nMnCEf2IFdEc571Tt+ESTTk5OimiheDyJms2PKf87GLRnarC89txY1C6RrFvHf3Ng\ndlKKIs70oDuqwX3nvpJFRUpk5xXnlWrya9957tdReWVgB3n2QHDjI0Apn+ZXM/wI\noL+dTQSXvR/DHCJMkAptyi6trQKBgQC7lJ9QapYh3InMfBjbPr04VRd3a5H4vhTM\nxkaNkuGhxNqqFI/1V91Ph+MS1+b3WtnKLodz0CYb10u+dSEXZTy5QFA3E4tMg4IQ\nFrpEWv6thQhTyF2eccmfIDBkNBRU0csBLhX69e5U7NmDr27xn3egawyWVn6V6BrR\nVMT0jRFSKQKBgBl1O8m3yTumlZoz+XsP0ZO2x2GxYTtpT/OtRmW3luUNq4qyPlB3\nC3xGMl+/hR+qHnjisYWPjhn4lKxxUPMStRlSQdBc44hU0jQ4I2LHKHDxoxRh0SUC\n4S9hS1yck62BT8ImBMoJgBQB9JjVaCQ8IR7Pciwh+nH25xL6fGbKuiKBAoGAaRjx\nVg4SBfDZqB9TkeuJ+vj6B+fWRmbBoqXou8Oy9X8lAKw6qDzNe5ToLhOXjblyUuxU\n6heScoDjKFfZ7ZDEQAr/powlvP3lrnv9avUMwk3KB584jOC2FZjkZBAl4AwXUJbw\nq8aE/UIi8LwnTeuKC/BOgiD+FaGQ/P4gx+AN91kCgYAThhxMDT5OUxlLmF7c4dQ2\nHJX/qVTS/H4vkum64Omcs09/GHz7sY/i749TWu0Km4Wd+KhFmW2+TmyKJ4TaYcpG\njM7o1Q9EnL5Rota1a8AzeOXDOMoOa/OcJyP/4/Gxg2u5SxgN5OPVKd/Xj4IoN7y0\n8mOsFzoLxT9D3+6mlu8kEw==\n-----END PRIVATE KEY-----\n",
        "client_email": "test-491@trackabull.iam.gserviceaccount.com",
        "client_id": "106268402368715574175",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test-491%40trackabull.iam.gserviceaccount.com"
    }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        credentials_dict
    )
    client = storage.Client(credentials=credentials, project='TrackABull')
    bucket = client.get_bucket('imgdet')

    while True:
        #img = cap.read()
        imgBlob = bucket.get_blob('image.jpg')
        s = imgBlob.download_as_string()
        nparr = np.frombuffer(s, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        img = cv2.resize(img_np, (1280, 720))
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