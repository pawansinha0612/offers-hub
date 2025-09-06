from flask import Flask, jsonify, request
from flask_cors import CORS
import csv
import os

app = Flask(__name__)
CORS(app)

def read_csv(file_path):
    data = []
    if not os.path.exists(file_path):
        return data
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

@app.route("/offers")
def offers():
    source = request.args.get("source", "all").lower()
    data = []

    if source in ["all", "shopback"]:
        data.extend(read_csv("backend/sources/shopback/shopback_offers.csv"))

    # Future: add more sources here like cashrewards, honey, etc.

    return jsonify(data)

@app.route("/")
def home():
    return "Offers-Hub Backend is running. Go to /offers to see data."

if __name__ == "__main__":
    app.run(debug=True)
