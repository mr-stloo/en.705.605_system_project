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

Accessing the Web GUI
---------------------
1) Create an environment with following libraries:
    - Python 3.6
    - pip3 install kafka-python 
    - pip3 install pymongo
    - pip3 install sklearn
    - pip3 install keras==2.3 
    - pip3 install tensorflow==2.2
    - pip3 install django
    - pip3 install djongo
    - pip3 install numpy
    - pip3 install opencv-python
    - pip3 install pillow

2) Download GitHub files into a folder such as c:\temp
3) Open terminal of the environment 
4) cd into c:\temp\mysite
5) Start up the web application:
        
        python manage.py runserver

6) Open browser: http://localhost:8000/loadtarget/admin/


To start streaming videos and tracking:
---------------------------------------
1) 

