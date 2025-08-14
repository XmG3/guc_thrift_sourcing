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
        # eBay validation step: challenge_code comes as query param
        challenge_code = request.args.get("challenge_code", "")
        # Compute hash: SHA256(challengeCode + verificationToken + endpointURL)
        combined = (challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL).encode('utf-8')
        response_hash = hashlib.sha256(combined).hexdigest()
        return jsonify({"challengeResponse": response_hash}), 200

    elif request.method == "POST":
        # Real account deletion notification from eBay
        notification = request.get_json()
        print("Received deletion notification:", notification)
        # TODO: delete user data here, if you store any
        return Response(status=200)

    # For any other method
    return Response(status=400)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
