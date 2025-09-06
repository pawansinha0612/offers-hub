import os
from flask import Flask, jsonify
from flask_cors import CORS
import csv

app = Flask(__name__)
CORS(app)

# Always resolve CSV path relative to this script
CSV_PATH = os.path.join(os.path.dirname(__file__), "sources/shopback/shopback_offers.csv")

@app.route("/offers")
def offers():
    data = []
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        return {"error": str(e)}, 500
    return jsonify(data)

@app.route("/")
def home():
    return "Flask backend is running. Go to /offers to see data."

if __name__ == "__main__":
    app.run(debug=True)
