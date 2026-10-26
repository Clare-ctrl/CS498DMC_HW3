import os
from pymongo import MongoClient
from pymongo.write_concern import WriteConcern
from pymongo import ReadPreference
from flask import Flask, request, jsonify

app = Flask(__name__)

client = MongoClient(os.environ["MONGO_URI"])
collection = client["ev_db"]["vehicles"]
collection.create_index("Make")

@app.route("/")
def home():
    return "HW3 API is running! "

# POST / insert-fast
@app.route("/insert-fast", methods=["POST"])
def insert_fast():
    data = request.get_json(silent=True)

    if not data or not isinstance(data, dict):
        return jsonify({"error": "No valid JSON Object provided"}), 400
    try:
        clean_data = {
            k: v.strip() if isinstance(v, str) else v
            for k, v in data.items()
        }
        coll = collection.with_options(write_concern=WriteConcern(w=1))
        result = coll.insert_one(clean_data)

        return jsonify({
            "inserted_id" : str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST / insert-safe
@app.route("/insert-safe", methods=["POST"])
def insert_safe():
    data = request.get_json(silent=True)

    if not data or not isinstance(data, dict):
        return jsonify({"error": "No valid JSON Object provided"}), 400
    try:
        clean_data = {
            k: v.strip() if isinstance(v, str) else v
            for k, v in data.items()
        }
        coll = collection.with_options(write_concern=WriteConcern(w="majority"))
        result = coll.insert_one(clean_data)

        return jsonify({
            "inserted_id" : str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get / count-tesla-primary
@app.route("/count-tesla-primary", methods=["GET"])
def count_tesla_primary():

    try:
        coll = collection.with_options(read_preference=ReadPreference.PRIMARY)
        n = coll.count_documents({"Make": "TESLA"})

        return jsonify({
            "count": n
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get / count-bmw-secondary
@app.route("/count-bmw-secondary", methods=["GET"])
def count_bmw_secondary():

    try:
        coll = collection.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
        n = coll.count_documents({"Make": "BMW"})

        return jsonify({
            "count": n
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)