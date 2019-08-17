from flask import Flask, render_template, send_file, request, make_response
import os
import multiprocessing as mp


_DIRPATH = os.path.dirname(os.path.abspath(__file__))


APP = Flask("__main__", template_folder=os.path.join(_DIRPATH, "static"))
APP.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


QUEUE = mp.Queue()


@APP.route("/")
def index():
    return render_template("index.html")


@APP.route("/static/<string:filename>")
def static_file(filename):
    filepath = os.path.join(_DIRPATH, "static", filename)
    if os.path.exists(filepath):
        return send_file(filepath)


@APP.route("/api", methods=["POST"])
def alive():
    body = request.get_json()
    print(body)
    QUEUE.put(body)
    return make_response()


if __name__ == "__main__":
    APP.run("0.0.0.0", 5000)
