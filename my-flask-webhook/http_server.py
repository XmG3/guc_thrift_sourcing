from flask import Flask, request, jsonify, Response
import hashlib

# Replace these with your actual values
VERIFICATION_TOKEN = "dznrOg44uA4NewgrbkYEvGn2srsrpOIi"
ENDPOINT_URL = "https://fe681c91b7b6.ngrok-free.app/account-deletion"  # without trailing slash

app = Flask(__name__)

@app.route("/")
def index():
    return "ebay endpoint is running"
    #main page placeholder

@app.route("/account-deletion", methods=["GET", "POST"])
@app.route("/account-deletion/", methods=["GET", "POST"])

def account_deletion():
    if request.method == "GET":
        return "Validation successful", 200
    elif request.method == "POST":
        data = request.get_json()
        # optional: process deletion data here
        return "", 200

    # For any other method
    return Response(status=400)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
