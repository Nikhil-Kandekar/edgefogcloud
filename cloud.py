from flask import Flask, request, jsonify
import time
import pymongo

app = Flask(__name__)

# Setup MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["edge_fog_cloud"]
collection = db["detections"]

@app.route("/save", methods=["POST"])
def save_to_db():
    start_time = time.time()
    data = request.json.get("data", "")

    collection.insert_one({"timestamp": time.time(), "detections": data})

    end_time = time.time()
    storage_latency = end_time - start_time

    return jsonify({"storage_latency": storage_latency})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
