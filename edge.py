import cv2
import requests
import time
import matplotlib.pyplot as plt
from numpy import random
from time import sleep

sleeptime = 0

FOG_SERVER = "http://34.93.203.181:5001/process"  # Update with actual Fog IP
CLOUD_SERVER = "http://34.131.20.117:5002/save"  # Update with actual Cloud IP

def capture_image(img_name):
    start_time = time.time()
    img = cv2.imread(img_name)  
    img = cv2.resize(img, (640, 480))  
    end_time = time.time()
    return img, end_time - start_time  

def preprocess_image(img):
    start_time = time.time()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  
    sleep(sleeptime)
    end_time = time.time()
    return gray, end_time - start_time  

def send_to_fog(img):
    start_time = time.time()
    _, img_encoded = cv2.imencode(".png", img)
    response = requests.post(FOG_SERVER, files={"file": img_encoded.tobytes()})
    fog_processing_time = response.json().get("processing_latency", 0)
    
    cloud_response = requests.post(CLOUD_SERVER, json={"data": response.json()})
    cloud_storage_time = cloud_response.json().get("storage_latency", 0)
    
    end_time = time.time()
    return (
        response.json(), 
        fog_processing_time, 
        cloud_storage_time,
        end_time - start_time  # Transmission and round-trip latency
    )

capture_times = []
preprocess_times = []
transmission_times = []
fog_processing_times = []
cloud_storage_times = []
total_latencies = []

imagelist = ["1.png", "2.png", "3.png"]
for img_name in imagelist:
    for _ in range(100):  
        img, cap_time = capture_image(img_name)
        preprocessed, prep_time = preprocess_image(img)
        result, fog_proc_time, cloud_store_time, trans_time = send_to_fog(preprocessed)

        total_latency = cap_time + prep_time + trans_time + fog_proc_time + cloud_store_time

        capture_times.append(cap_time)
        preprocess_times.append(prep_time)
        transmission_times.append(trans_time)
        fog_processing_times.append(fog_proc_time)
        cloud_storage_times.append(cloud_store_time)
        total_latencies.append(total_latency)

plt.figure(figsize=(10, 5))
plt.plot(capture_times, label="Capture Latency", linestyle='--', marker='o', markersize=3)
plt.plot(preprocess_times, label="Preprocessing Latency", linestyle='--', marker='x', markersize=3)
plt.plot(transmission_times, label="Transmission Latency", linestyle='--', marker='s', markersize=3)
plt.plot(fog_processing_times, label="Fog Processing Latency", linestyle='--', marker='d', markersize=3)
plt.plot(cloud_storage_times, label="Cloud Storage Latency", linestyle='--', marker='^', markersize=3)
plt.plot(total_latencies, label="Total Latency", linewidth=2)

plt.xlabel("Iterations")
plt.ylabel("Latency (s)")
plt.title("Latency Breakdown over 100 Runs")
plt.legend()
plt.grid()
plt.show()
