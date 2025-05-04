from flask import Flask, render_template, jsonify, g
import os
import sqlite3

imagesPath = "static/images"
imagesList = os.listdir(imagesPath)
imagesList = [img for img in imagesList if not img.endswith(".txt")]
imageIndex = 0
DATABASE = "./tags.db"


app = Flask(__name__)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.route("/")
def main():
    cur = get_db().cursor()
    res = cur.execute("select * from tags;").fetchall()
    return res
    # return "Image Tagger!"


@app.route("/tag")
def tagger():
    firstImage = imagesList[0]
    return render_template(
        "imagetagger.html", imagesPath=imagesPath, currentImage=firstImage
    )


@app.route("/nextImage")
def next():
    global imageIndex
    if imageIndex != (len(imagesList) - 1):
        next_image = jsonify(imagesList[imageIndex + 1])
        imageIndex += 1
        return next_image
    else:
        return jsonify(imagesList[imageIndex])


@app.route("/prevImage")
def previousImage():
    global imageIndex
    if imageIndex != 0:
        previous_image = jsonify(imagesList[imageIndex - 1])
        imageIndex -= 1
        return previous_image
    else:
        return jsonify(imagesList[imageIndex])


@app.teardown_appcontext
def close_connection(e):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
