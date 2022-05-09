# THIS PYTHON FILE SIMULATE CAMERA FEEDING FACIAL IMAGES (USING KAFKA TOPICS) TO A PROCESSOR CODE THAT COMPUTES THE DISTANCE BETWEEN EMBEDDINGS.
# HOW TO RUN THIS PYTHON FILE, EXAMPLE:
#
#       python camera.py ".\\input\\videos\\The_Sound_of_Music_clip.mp4" 100 "Room 1" false
#
# First argument  : Video input file to simulate live camera recording.
# Second argument : Width and height size in pixel for facial size to be considered for embedding comparison. Smaller value means ignoring faces that are too small in images (or videos);
#                   Valid valid: 50 <= size <= 100.          
# Third argument  : Label for camera/location.
# Fourth argument : 'false' means simulating without using Kafka messaging. I am struggling to get Kafka working as I desired, it does work though. 'true' means running using Kafka messaging.


import cv2
import sys
import tensorflow as tf
from numpy import load
from numpy import expand_dims
from numpy import asarray
import numpy as np
from sklearn.preprocessing import Normalizer
from sklearn.metrics.pairwise import euclidean_distances
from keras.models import load_model
from cv2 import CascadeClassifier
from PIL import Image
from IPython.display import display # to display images
from IPython.display import Video
from json import dumps  
from kafka import KafkaProducer
import pymongo
from datetime import datetime
from sklearn.metrics.pairwise import euclidean_distances


# load the models
GLOBAL_facenet_model = load_model('.\\pre-trained\\facenet_keras.h5', compile=False)
GLOBAL_face_finder = CascadeClassifier('.\\pre-trained\\haarcascade_frontalface_default.xml')
CONFIG_INI_FILE = ".\\mysite\\config.ini"
STATUS_FILE = ".\\mysite\\START"
UPDATE_CONFIG_FILE = ".\\mysite\\UPDATED_CONFIG"
UPDATE_DB_FILE =  ".\\mysite\\UPDATED_DB"
STORAGE_LOCATION = ".\\mysite"


threshold = 0.5
mode = "average"
target_embeddings = []
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydb"]
target_table=mydb["target"]
log_table=mydb["log"]


my_producer = KafkaProducer(  
    bootstrap_servers = ['localhost:29092'],  
    value_serializer = lambda x:dumps(x).encode('utf-8')  
)


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


def read_config_ini():
    print("Reading config.ini...")
    global mode
    global threshold
    f = open(CONFIG_INI_FILE,"r")
    threshold = float(f.readline())
    mode = f.readline()
    f.close()


def load_embeddings():
    print("Loading embeddings...")
    target_list = list(target_table.find({}))
    target = []
    for i in range(0,len(target_list)):
        data = np.load(STORAGE_LOCATION + target_list[i]["file_location"])
        target.append([target_list[i]["name"],data["pic1"],data["pic2"],data["pic3"],data["avg"]])
    return target


def compare_embeddings(arr):
    global mode
    global threshold
    global target_embeddings
    input_embedding = np.array(arr["num"][4])
    if mode == "average":
        for t in target_embeddings:            
            result = euclidean_distances([t[4]],[input_embedding])
            if result[0][0] <= threshold:           
                data = {"date": arr["num"][0], "time": arr["num"][1], "playback": arr["num"][2],
                 "location": arr["num"][3],"name": t[0],"video": arr["num"][5],
                 "mode":mode, "threshold":threshold, "distance":round(result[0][0],2)}
                log_table.insert_one(data)
                print("Detected:", t[0], "; Distance=%.2f" % (result[0][0]))     
    else:
        for t in target_embeddings:            
            result = min(euclidean_distances([t[1]],[input_embedding]),
                         euclidean_distances([t[2]],[input_embedding]),
                         euclidean_distances([t[3]],[input_embedding]))
            if result[0][0] <= threshold:
                data = {"date": arr["num"][0], "time": arr["num"][1], "playback": arr["num"][2],
                 "location": arr["num"][3],"name": t[0],"video": arr["num"][5],
                 "mode":mode, "threshold":threshold, "distance":round(result[0][0],2)}
                log_table.insert_one(data)                
                print("Detected:", t[0], "; Distance=%.2f" % (result[0][0]))     


def load_embeddings():
    print("Loading targets embeddings from database...")
    target_list = list(target_table.find({}))
    target = []
    for i in range(0,len(target_list)):
        data = np.load(STORAGE_LOCATION + target_list[i]["file_location"])
        target.append([target_list[i]["name"],data["pic1"],data["pic2"],data["pic3"],data["avg"]])
    return target


def send_message(msg):
    my_data = {'num' : msg}                            
    my_producer.send('testnum', value = my_data)


def main():
    global target_embeddings
    inputVideo = sys.argv[1]
    box_size = int(sys.argv[2])
    if box_size < 50:
        box_size = 50
    elif box_size > 100:
        box_size = 100
    cam = sys.argv[3].lower()
    mode = sys.argv[4].lower()
    video = cv2.VideoCapture(inputVideo)
    if (video.isOpened()== False):
        sys.exit("Error opening video stream or file")   
    fps = video.get(cv2.CAP_PROP_FPS)
    size = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)),int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    print("\n\n\nPress 'Q' to stop anytime.\n\n")
    print("\nVideo size:",size,"; Frame count:", num_frames, "; FPS:",fps)
    if mode == "false":
        read_config_ini()
        target_embeddings = load_embeddings()
        print("Running demo 'without' using Kafka Messaging...")
        mytask = compare_embeddings
    else:
        print("\nAttempting to run demo using Kafka Messaging... NOTE: Could take sometime for consumer (processor.py) to received message.")
        print("NOTE: Must run 'processor.py' as Kafka consumer.\n\n")
        mytask = send_message
    frame_count = 0    
    while(video.isOpened()):
        ret, frame_array = video.read()
        if ret == True:
            # Process 2 frames every 1 second.
            if frame_count % fps/2==0:
                bboxes = GLOBAL_face_finder.detectMultiScale(frame_array,1.10,20)
                # print bounding box for each detected face
                for box in bboxes:
                    x1, y1, width, height = box
                    x2, y2 = x1 + width, y1 + height
                    # draw a rectangle over the pixels
                    try:
                        if width >= box_size and height >= box_size:
                            cv2.rectangle(frame_array, (x1, y1), (x2, y2), (0,0,255), 1)
                            clipped_img_array = frame_array[y1:y2, x1:x2]
                            resized_face_array = resize_array(clipped_img_array)
                            time_in_second = float(frame_count)/fps
                            datestamp = datetime.now().strftime("%m-%d-%Y")
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            embedding = get_embedding(resized_face_array)                          
                            embedding_list = embedding.tolist()
                            mytask({'num' : [datestamp,timestamp,time_in_second, cam, embedding_list, inputVideo]})
                    except:
                        video.release()
                        cv2.destroyAllWindows()
                        sys.exit("Something failed...")                        
                cv2.imshow('Frame',frame_array)            
            # Press Q on keyboard to  exitq
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break
        frame_count+=1    
    video.release()
    cv2.destroyAllWindows()
    print("\nExited\n\n")
    

if __name__ == "__main__":
    main()

    

