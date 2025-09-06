from flask import Flask, jsonify
from flask_cors import CORS
import csv
import os

app = Flask(__name__)
CORS(app)

CSV_PATH = os.path.join(os.path.dirname(__file__), "sources/shopback/shopback_offers.csv")

@app.route("/offers")
def offers():
    data = []
    try:
        print(f"Reading CSV from: {CSV_PATH}")  # log path
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        print(f"Loaded {len(data)} offers")  # log number of offers
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {"error": str(e)}, 500
    return jsonify(data)

@app.route("/")
def home():
    return "Flask backend is running. Go to /offers to see data."

if __name__ == "__main__":
    print("Starting Flask app")
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
