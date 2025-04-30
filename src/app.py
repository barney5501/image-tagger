from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def main():
    return "Image Tagger!"


@app.route("/tag")
def tagger():
    return render_template("imagetagger.html")
