from flask import Flask, request
from flask_cors import CORS





def server_receiver():
    app = Flask(__name__)
    CORS(app) 

    @app.route("/receive", methods=["POST"])
    def receive():
        data = request.json
        print("Got:", data)
        return {"ok": True}

    app.run(port=8000)