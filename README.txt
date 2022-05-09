
https://www.mongodb.com/compatibility/docker

docker pull mongo:latest

docker run --name mongodb -d -p 27017:27017 mongo


Create host directories:
1) mkdir C:\temp\nosql\mongo
2) mkdir C:\temp\nosql\mongo\import
3) mkdir C:\temp\nosql\mongo\data

docker run --name mongodb -d -p 27017:27017 -v C:/temp/nosql/mongo/data:/data/db -v C:/temp/nosql/mongo/import:/import mongo

docker run --name mongodb -d --network mynetwork mongo

docker run --name my_system_project -d -p 8000:8000 -v C:/temp/nosql/mongo/data:/data/db -v C:/temp/nosql/mongo/import:/import sloo/myclass:en.705.605_system_project1



install:


pip install keras==2.3 
pip install tensorflow==2.2		<---------- must be after KERAS
pip install kafka-python 
pip install django-background-tasks (do not need)
pip install django-cleanup (do not need)
pip install pymongo


Kafka server:
=============
Create "docker-compose.yml" - see file in "C:\Users\ST\Documents\OneDrive - Johns Hopkins\EN.705.603\System_Project"
Run command: docker-compose up -d  (this will Pull Kafka & Zookeeper, then run the container)
Command to check connections: 
->		test-netconnection localhost -port 29092
->		test-netconnection localhost -port 22181