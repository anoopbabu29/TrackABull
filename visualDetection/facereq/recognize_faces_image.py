# USAGE
# python recognize_faces_image.py --encodings encodings.pickle --image examples/example_01.png 

# import the necessary packages
import face_recognition
import argparse
import pickle
import cv2

def detectFaces(image, data, method = "hog"):
	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	boxes = face_recognition.face_locations(rgb, model=method)
	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []

	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)

		# check to see if we have found a match
		if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number of
			# votes (note: in the event of an unlikely tie Python will
			# select first entry in the dictionary)
			name = max(counts, key=counts.get)
			names.append(name)
		
		# update the list of names

	return names