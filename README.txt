Instructions for setting up MongoDB server:
-------------------------------------------
1) docker pull mongo:latest
2) docker run --name mongodb -d -p 27017:27017 mongo
3) Create host directories:
    mkdir C:\temp\nosql\mongo
    mkdir C:\temp\nosql\mongo\import
    mkdir C:\temp\nosql\mongo\data
4) docker run --name mongodb -d -p 27017:27017 -v C:/temp/nosql/mongo/data:/data/db -v C:/temp/nosql/mongo/import:/import mongo


Instructions for setting up Kafka server:
-----------------------------------------
1) Download 'docker-compose.yml' from GitHub.
2) docker-compose up -d
3) Command to test connections (in Windows):
    test-netconnection localhost -port 29092
    test-netconnection localhost -port 22181

Accessing the Web GUI (make sure MongoDB and Kafka are up first):
-----------------------------------------------------------------
1) Create an environment with following libraries:
    - Python 3.6
    - pip3 install kafka-python 
    - pip3 install pymongo
    - pip3 install sklearn
    - pip3 install keras==2.3 
    - pip3 install tensorflow==2.2          <---------- DO NOT install before Keras 2.3
    - pip3 install django
    - pip3 install djongo
    - pip3 install numpy
    - pip3 install opencv-python
    - pip3 install pillow
    - pip3 install mtcnn

2) Download GitHub files into a folder c:\temp\track  <---------- create C:\temp\track if does not exists.
3) Open terminal of the environment 
4) cd into c:\temp\track\mysite
5) Start up the web application:
        
        python manage.py runserver

6) Open browser: http://localhost:8000/loadtarget/admin/


To start streaming videos and tracking:
---------------------------------------
1) Open another terminal of the environment.

2) cd into C:\temp\track

3) Start video streaming:

    OPTION 1 (using Kafka): 
              
              python camera.py ".\\input\\videos\\The_Sound_of_Music_clip.mp4" 100 "Room 1" true     
              
              python processor.py               (in new terminal)
    
    OPTION 2 (without): 
    
            python camera.py ".\\input\\videos\\The_Sound_of_Music_clip.mp4" 100 "Room 1" false  
    
    Check web GUI 'Dashboard' for update.
    
    NOTES: 
    # more videos in C:\temp\track\input\videos
    # First argument  : Video input file to simulate live camera recording.
    # Second argument : Width and height size in pixel for facial size to be considered for embedding comparison. Smaller value means ignoring faces that are too small in images (or videos);
    #                   Valid valid: 50 <= size <= 100.          
    # Third argument  : Label for camera/location.
    # Fourth argument : 'false' means simulating without using Kafka messaging. I am struggling to get Kafka working as I desired, it does work though. 'true' means running using Kafka messaging.
    
 
 
 

