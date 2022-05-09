import sys
import logging
from django.apps import AppConfig
from tensorflow.keras.models import load_model
#from keras.models import load_model
from cv2 import CascadeClassifier
from django.conf import settings

GLOBAL_facenet_model = None
GLOBAL_face_finder = None


class LoadtargetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'loadtarget'
    if 'runserver' in sys.argv:
        logging.debug("\n--------- LOADING PRE-TRAINED MODELS ---------")
        global GLOBAL_facenet_model
        GLOBAL_facenet_model = load_model("..\\pre-trained\\facenet_keras.h5",compile=False)
        global GLOBAL_face_finder
        GLOBAL_face_finder = CascadeClassifier('.\\pre-trained\\haarcascade_frontalface_default.xml')
        logging.debug("\n--------- DONE LOADING PRE-TRAINED MODELS --------- \n")
        #background_thread = threading.Thread(target=compute_distance,name="compute_distance",)
        #background_thread.start()


