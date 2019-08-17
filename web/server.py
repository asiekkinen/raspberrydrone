from flask import Flask, Response, render_template, send_file, request, make_response
import os
import io
import time
from threading import Condition
import multiprocessing as mp
from drone.flight_controller.flight_controller import FlightController


dirpath = os.path.dirname(os.path.abspath(__file__))

# Flask related.
app = Flask("__main__", template_folder=os.path.join(dirpath, "static"))
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Flight controller related.
QUEUE = mp.Queue()
FLIGHT_CONTROLLER = None
FLIGHT_PROCESS = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/static/<string:filename>")
def static_file(filename):
    filepath = os.path.join(dirpath, "static", filename)
    if os.path.exists(filepath):
        return send_file(filepath)


@app.route("/api", methods=["POST"])
def alive():
    body = request.get_json()
    print(body)
    QUEUE.put(body)
    return make_response()


if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
