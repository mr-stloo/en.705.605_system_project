from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from loadtarget.forms import TargetForm
from loadtarget.models import Target
import logging
from . import facial_model
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib import messages
from django.conf import settings
from PIL import Image
import pymongo
import os
from os.path import exists

GLOBAL_isTracking = False

def view_target_list(request):
    UPDATE_DB_FILE = str(settings.BASE_DIR)+"\\UPDATED_DB"
    if request.method == 'POST':
        name_to_be_deleted =  request.POST.get('name')
        records = Target.objects.filter(name__iexact=name_to_be_deleted)        
        # Only expect one record though.
        for record in records:
            os.remove(str(settings.BASE_DIR)+ "\\storage\\"+ str(record.pic1).replace("/","\\"))
            os.remove(str(settings.BASE_DIR)+ "\\storage\\"+ str(record.pic2).replace("/","\\"))
            os.remove(str(settings.BASE_DIR)+ "\\storage\\"+ str(record.pic3).replace("/","\\"))
            os.remove(str(settings.BASE_DIR)+ "\\" + record.file_location)
        records.delete()
        f = open(UPDATE_DB_FILE,"w")
        f.write("UPDATED")    
        f.close()              
    persons = Target.objects.all()
    logging.debug("----------------------------------------------------------------------------------------------")
    for p in persons:
        logging.debug(p)
        logging.debug(p.pic1)
        logging.debug("============================================================")
    template = loader.get_template('view_target_list.html')
    context = {
        'targets': persons,
    }
    return HttpResponse(template.render(context, request))


def load_new_target(request):
    UPDATE_DB_FILE = str(settings.BASE_DIR)+"\\UPDATED_DB"
    if request.method == 'POST':
        form = TargetForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Target added to database successfully.')
                f = open(UPDATE_DB_FILE,"w")
                f.write("UPDATED")    
                f.close()          
            except Exception as err:
                messages.error(request, "Invalid form submission: " + str(err))
    else:
        form = TargetForm()
    return render(request, 'TargetForm.html', {'form' : form})

def dashboard(request):
    if request.method == 'GET':
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["mydb"]
        log_table = mydb["log"]
        target_table = mydb["target"]
        target_table_data = list(target_table.find({}))
        log_table_data = [] 
        # Find latest record based on date and time for each user. 
        for row in target_table_data:
            data = list(log_table.find({"name":row["name"]}).sort([("date",-1),("time",-1)]).limit(1))
            if data != []:
                log_table_data.append(data[0])            
        template = loader.get_template('dashboard.html')
        context = {
            'targets': log_table_data,
        }
        return HttpResponse(template.render(context, request))



def admin(request):
    global GLOBAL_isTracking
    #global GLOBAL_background_thread
    global GLOBAL_condition
    CONFIG_INI_FILE = str(settings.BASE_DIR)+"\\config.ini"
    STATUS_FILE = str(settings.BASE_DIR)+"\\START"
    UPDATE_CONFIG_FILE = str(settings.BASE_DIR)+"\\UPDATED_CONFIG"
    f = open(CONFIG_INI_FILE,"r")
    threshold = float(f.readline())
    mode = f.readline()
    f.close()
    if request.method == 'POST':
        if request.POST.get('config'):
            f = open(CONFIG_INI_FILE,"w")
            threshold = request.POST.get('threshold_value')
            mode = request.POST.get('comparison_mode')
            f.write(threshold + "\n")
            f.write(mode + "\n")    
            f.close()
            fu = open(UPDATE_CONFIG_FILE,"w")
            fu.write("UPDATED")    
            fu.close()            
        elif request.POST.get('start'):
            is_start = request.POST.get('start')
            if is_start == "True":
                GLOBAL_isTracking = True
                try:
                    f = open(STATUS_FILE,"w")
                    f.writelines("START")
                    f.close()
                except:
                    logging.debug("Cannot create file....")
            else:
                GLOBAL_isTracking = False
                try:
                    os.remove(STATUS_FILE)
                except:
                    logging.debug("Cannot remove STATUS_FILE...")    
    template = loader.get_template('admin.html')
    if mode.lower() == "average":
        if GLOBAL_isTracking == True:
            context = {'threshold': threshold, 'is_start': True, }
        else:
            context = {'threshold': threshold,}
    else:                
        if GLOBAL_isTracking == True:
            context = {'threshold': threshold,'mode': "minimum", 'is_start': True, }
        else:
            context = {'threshold': threshold,'mode': "minimum", }
    return HttpResponse(template.render(context, request))

    