from numpy import load
from numpy import expand_dims
from numpy import asarray
from numpy import savez_compressed
from sklearn.preprocessing import Normalizer
from sklearn.metrics.pairwise import euclidean_distances

import os
import cv2
from cv2 import CascadeClassifier
import mtcnn
import tensorflow as tf
from PIL import Image
import logging
from loadtarget.apps import GLOBAL_facenet_model, GLOBAL_face_finder




# Resize array of face.
def resize_array(input_img_array, required_size=(160, 160)):
    input_img = Image.fromarray(input_img_array)
    input_img = input_img.resize(required_size)
    resized_face_array = asarray(input_img)
    return resized_face_array

# get the face embedding from input array.
def get_embedding(input_img_array):
    face_array = input_img_array.astype('float32')           
    mean, std = face_array.mean(), face_array.std()     # scale pixel values
    face_array = (face_array - mean) / std              # standardize pixel values across channels (global)
    samples = expand_dims(face_array, axis=0)           # transform face into one sample
    yhat = GLOBAL_facenet_model.predict(samples)        # make prediction to get embedding
    in_encoder = Normalizer(norm='l2')
    yhat = in_encoder.transform(yhat)
    return yhat[0]
 
# Return face image array.
def get_face_img_array(input_file):
    input_img = Image.open(input_file)
    input_img = input_img.convert('RGB')
    input_img_array = asarray(input_img)
    face = GLOBAL_face_finder.detectMultiScale(input_img_array,1.10,20)
    # Expecting one face in the image.
    if len(face) > 1 or len(face) == 0:
        return []
    else:
        #x1, y1, width, height = face  <-------------- This does not work in DJango. Not sure why. Works in Jupyter.
        x1 = face[0][0]
        y1 = face[0][1]
        width = face[0][2]
        height = face[0][3]
        x2, y2 = x1 + width, y1 + height
        logging.debug(input_file)
        clipped_img_array = input_img_array[y1:y2, x1:x2]
        resized_face_array = resize_array(clipped_img_array)
        return resized_face_array

def get_face_img_from_array(input_img_array):
    return Image.fromarray(input_img_array)


def save_embeddings(pic1_array, pic2_array, pic3_array, pathname):
    emb1 = get_embedding(pic1_array)
    emb2 = get_embedding(pic2_array)
    emb3 = get_embedding(pic3_array)
    avg_emb = (emb1 + emb2 + emb3) / 3
    savez_compressed(pathname, pic1=emb1, pic2=emb2,pic3=emb3, avg=avg_emb)











