from flask import Flask, request, Response
import hashlib
import os

# Replace with your actual eBay verification token
VERIFICATION_TOKEN = "dznrOg44uA4NewgrbkYEvGn2srsrpOIi"

# Full endpoint URL as registered in eBay (without trailing slash)
ENDPOINT_URL = "https://guc-thrift-sourcing.onrender.com/account-deletion"

app = Flask(__name__)

@app.route("/")
def index():
    return "eBay endpoint is running", 200

@app.route("/account-deletion", methods=["GET", "POST"])
def account_deletion():
    if request.method == "GET":
        # eBay validation
        challenge = request.args.get("challengeCode", "")
        if not challenge:
            return "Missing challengeCode", 400
        # Compute SHA-256 hash
        m = hashlib.sha256((challenge + VERIFICATION_TOKEN + ENDPOINT_URL).encode("utf-8"))
        return m.hexdigest(), 200

    elif request.method == "POST":
        # Handle actual deletion notifications
        data = request.get_json()
        print("Received deletion data:", data)
        # Optional: process the data (log, database, etc.)
        return "", 200

    # Any other method
    return Response(status=400)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)