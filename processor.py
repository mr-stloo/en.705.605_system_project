# importing the required modules  
from json import loads  
from kafka import KafkaConsumer
from os.path import exists
import numpy as np
import pymongo
from sklearn.metrics.pairwise import euclidean_distances

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
target_table = mydb["target"]
log_table = mydb["log"]

my_consumer = KafkaConsumer(  
    'testnum',  
        bootstrap_servers = ['localhost : 29092'],  
        auto_offset_reset = "latest", 
        enable_auto_commit = False,  
        group_id = 'my-group',  
        value_deserializer = lambda x : loads(x.decode('utf-8'))  
)

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
                #print(arr)
                #print(arr["num"][0])
                #print(arr["num"][1])
                #print(arr["num"][2])
                #print(arr["num"][3])
                #print(arr["num"][4])
                #print(arr["num"][5])
                data = {"date": arr["num"][0], "time": arr["num"][1], "playback": arr["num"][2],
                 "location": arr["num"][3],"name": t[0],"video": arr["num"][5],
                 "mode":mode, "threshold":threshold, "distance":round(result[0][0],2)}
                log_table.insert_one(data)                
                print("Detected:", t[0], "; Distance=%.2f" % (result[0][0]))     


# generating the Kafka Consumer  
def main():
    global target_embeddings
    read_config_ini()
    target_embeddings = load_embeddings()
    print("Waiting for Kafka messages. Could take some time...")
    for message in my_consumer:
        message = message.value
        compare_embeddings(message)

    
if __name__ == "__main__":
    main()

