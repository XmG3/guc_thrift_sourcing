from flask import Flask, request, Response
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
            challenge = request.args.get("challengeCode")
            
            if not challenge:
                logger.error("Missing challengeCode in GET request")
                return Response("Missing challengeCode", status=400)
            
            logger.info(f"Received challenge code: {challenge}")
            
            # Compute SHA-256 hash as per eBay specification
            hash_string = challenge + VERIFICATION_TOKEN + ENDPOINT_URL
            logger.info(f"Hash string: {hash_string}")
            
            m = hashlib.sha256(hash_string.encode("utf-8"))
            response_hash = m.hexdigest()
            
            logger.info(f"Generated hash: {response_hash}")
            
            # Return plain text response
            return Response(response_hash, status=200, mimetype='text/plain')
        
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