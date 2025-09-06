from flask import Flask, jsonify
from flask_cors import CORS
import csv

app = Flask(__name__)
CORS(app)  # allow React to access

@app.route("/offers")
def offers():
    data = []
    try:
        with open("sources/shopback/shopback_offers.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        return {"error": str(e)}, 500
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
