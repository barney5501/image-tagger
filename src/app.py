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


@app.route("/image/<direction>")
def navigateImages():
    global imageIndex
    directions = {"prev": -1, "next": 1}
    direction = directions[direction]
    if imageIndex not in [len(imagesList) - 1, 0]:
        requested_image = imagesList[imageIndex + direction]
        tags = get_tags(requested_image)
        res = {"image": requested_image, "tags": tags}
        imageIndex += direction
        return jsonify(res)
    else:
        return ("", 204)


@app.route("/nextImage")
def nextImage():
    global imageIndex
    if imageIndex != (len(imagesList) - 1):
        next_image = imagesList[imageIndex + 1]
        tags = get_tags(next_image)
        res = {"image": next_image, "tags": tags}
        imageIndex += 1
        return jsonify(res)
    else:
        return ("", 204)


@app.route("/prevImage")
def previousImage():
    global imageIndex
    if imageIndex != 0:
        previous_image = imagesList[imageIndex - 1]
        tags = get_tags(previous_image)
        res = {"image": previous_image, "tags": tags}
        imageIndex -= 1
        return jsonify(res)
    else:
        return ("", 204)


def get_tags(img_name):
    cur = get_db().cursor()
    tag_query = f"select tag from tags where path = '{img_name}'"

    tags = cur.execute(tag_query).fetchall()
    image_tags = [tag for tagtuple in tags for tag in tagtuple]
    return image_tags


@app.teardown_appcontext
def close_connection(e):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
