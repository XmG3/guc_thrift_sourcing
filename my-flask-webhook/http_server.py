from flask import Flask, request, Response, jsonify
import hashlib
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    try:
        if request.method == "GET":
            # eBay validation request
            challenge_code = request.args.get("challenge_code")
            
            if not challenge_code:
                logger.error("Missing challenge_code in GET request")
                logger.error(f"Query params received: {request.args}")
                return Response("Missing challenge_code", status=400)
            
            logger.info(f"Received challenge code: {challenge_code}")
            
            # Compute SHA-256 hash as per eBay specification
            # Order: challengeCode + verificationToken + endpoint
            hash_string = challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL
            logger.info(f"Hash string: {hash_string}")
            
            m = hashlib.sha256(hash_string.encode("utf-8"))
            response_hash = m.hexdigest()
            
            logger.info(f"Generated hash: {response_hash}")
            
            # Return JSON response with challengeResponse field
            response_data = {"challengeResponse": response_hash}
            
            return jsonify(response_data), 200, {'Content-Type': 'application/json'}
        
        elif request.method == "POST":
            # Handle actual deletion notifications
            try:
                data = request.get_json(force=True)
                logger.info(f"Received deletion notification: {data}")
                
                # Process the data as needed
                # You should implement your business logic here
                
                # eBay expects a 200 OK response
                return Response("", status=200)
                
            except Exception as e:
                logger.error(f"Error processing POST request: {str(e)}")
                return Response("Internal server error", status=500)
    
    except Exception as e:
        logger.error(f"Unexpected error in account_deletion: {str(e)}")
        return Response("Internal server error", status=500)

# Health check endpoint
@app.route("/health")
def health_check():
    return {"status": "healthy"}, 200

# Test endpoint to verify hash calculation manually
@app.route("/test-hash")
def test_hash():
    # For testing purposes - remove in production
    test_challenge = "test123"
    hash_string = test_challenge + VERIFICATION_TOKEN + ENDPOINT_URL
    m = hashlib.sha256(hash_string.encode("utf-8"))
    response_hash = m.hexdigest()
    
    return {
        "test_challenge": test_challenge,
        "verification_token": VERIFICATION_TOKEN,
        "endpoint_url": ENDPOINT_URL,
        "hash_string": hash_string,
        "response_hash": response_hash
    }

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return Response("Not found", status=404)

@app.errorhandler(500)
def internal_error(error):
    return Response("Internal server error", status=500)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)