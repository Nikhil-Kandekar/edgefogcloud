from flask import Flask, request, jsonify
import cv2
import numpy as np
import time
import torch
from yolov5 import YOLOv5
import requests

app = Flask(__name__)

MODEL = YOLOv5("yolov5s.pt")  
CLOUD_SERVER = "http://34.131.253.152:5002/save"  # Cloud endpoint

@app.route("/process", methods=["POST"])
def process_image():
    recv_time = time.time()
    file = request.files["file"].read()
    nparr = np.frombuffer(file, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    process_start = time.time()

    results = MODEL.predict(img)
    process_end = time.time()

    detections = str(results)
    processing_latency = process_end - process_start

    cloud_response = requests.post(CLOUD_SERVER, json={"data": detections})
    cloud_storage_time = cloud_response.json().get("storage_latency", 0)

    return jsonify({
        "detections": detections,
        "processing_latency": processing_latency,
        "cloud_storage_time": cloud_storage_time,
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
