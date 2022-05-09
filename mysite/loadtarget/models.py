from logging import raiseExceptions
from django.db import models as dm
from djongo import models
from . import facial_model
import logging
import string

from . import facial_model
from django.conf import settings

# For preprocess_images function:
from django.core.files import File
from io import BytesIO
from datetime import datetime

def preprocess_images(image):
    face_array = facial_model.get_face_img_array(image)
    if face_array == []:
        return None, []
    mod_image = facial_model.get_face_img_from_array(face_array)
    myfile_io = BytesIO() # create a BytesIO object
    mod_image.save(myfile_io, 'JPEG') # save image to BytesIO object
    now = datetime.now()
    prefix = now.strftime("%m%d%Y_%H%M%S_")
    new_file_name = prefix + image.name
    mod_image_to_save = File(myfile_io, new_file_name) # create a django friendly File object
    return mod_image_to_save, face_array


# Create your models here.
class Target(models.Model):
    name = models.CharField(max_length = 200)
    # If time permit, implement check to validate file content to make sure they are valid input files.
    pic1 = models.ImageField(upload_to = 'uploads/',blank=True,null=True)
    pic2 = models.ImageField(upload_to = 'uploads/',blank=True,null=True)
    pic3 = models.ImageField(upload_to = 'uploads/',blank=True,null=True)
    file_location = models.CharField(max_length = 500)
    
    class Meta:
        db_table = "target"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # case insensitivity search.
        entry = Target.objects.filter(name__iexact=self.name)
        if len(entry) > 0:
            raise ValueError("Name: Individual with same name already exists in database.")
        else:
            if self.pic1 != None:
                self.pic1, img_array1 = preprocess_images(self.pic1)
                if self.pic1 == None:
                    raise ValueError("Pic 1: Invalid input.")
            else:
                raise ValueError("Pic 1: Invalid input.")
            if self.pic2 != None:
                self.pic2, img_array2 = preprocess_images(self.pic2)
                if self.pic2 == None:
                    raise ValueError("Pic 2: Invalid input.")
            else:
                raise ValueError("Pic 2: Invalid input.")
            if self.pic3 != None:    
                self.pic3, img_array3 = preprocess_images(self.pic3)
                if self.pic3 == None:
                    raise ValueError("Pic 3: Invalid input.")
            else:
                raise ValueError("Pic 3: Invalid input.")
            if self.pic1 != None and self.pic2 != None and self.pic3 != None:
                now = datetime.now()
                prefix = now.strftime("%m%d%Y_%H%M%S_")
                relative_npz_file_path = "\\storage\\" + prefix + str(self.name).replace(" ","") + ".npz"
                absolute_npz_file_path = str(settings.BASE_DIR) + "\\storage\\" + prefix + str(self.name).replace(" ","") + ".npz"
                facial_model.save_embeddings(img_array1,img_array2,img_array3,absolute_npz_file_path)
                self.file_location = relative_npz_file_path
                super().save(*args, **kwargs)

