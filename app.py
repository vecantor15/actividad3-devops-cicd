import os

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def index():
    return jsonify(
        application="devops-web-lab",
        message="Actividad 3 - CI/CD con GitHub Actions y Jenkins",
        version=os.getenv("APP_VERSION", "dev"),
    )


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.errorhandler(404)
def not_found(_error):
    return jsonify(error="not_found"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
