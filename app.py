from flask import Flask, jsonify
import os

app = Flask(__name__)
VERSION = os.environ.get("APP_VERSION", "1.0")
ENV = os.environ.get("APP_ENV", "blue")

@app.route('/')
def home():
    return jsonify({"message": f"Hello from {ENV} environment!", "version": VERSION})

@app.route('/health')
def health():
    return jsonify({"status": "ok", "env": ENV})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
