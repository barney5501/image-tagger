from flask import Flask, render_template, jsonify, g, request
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
    res = cur.execute("SELECT * FROM tags;").fetchall()
    return res
    # return "Image Tagger!"


@app.route("/tag")
def tagger():
    firstImage = imagesList[0]
    return render_template(
        "imagetagger.html", imagesPath=imagesPath, currentImage=firstImage
    )


@app.route("/image/<direction>")
def navigateImages(direction):
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
    tag_query = f"SELECT tag FROM tags WHERE path = '{img_name}'"

    tags = cur.execute(tag_query).fetchall()
    image_tags = [tag for tagtuple in tags for tag in tagtuple]
    return image_tags


@app.route("/image/<image>/tags", methods=["POST"])
def add_tag(image):
    if image not in imagesList:
        return (f"Sorry, image {image} does not exist!", 404)
    cur = get_db().cursor()
    image_tags = get_tags(img_name=image)
    tags = request.json
    insert_tags = [
        (image, tag.lower().strip())
        for tag in tags
        if tag.lower().strip() not in image_tags
    ]
    if len(insert_tags) == 0:
        return ("no new tags to add", 409)
    cur.executemany("INSERT INTO tags VALUES(?,?)", insert_tags)
    get_db().commit()
    return ("tags added", 200)


@app.route("/image/<image>/tags/<tag>", methods=["DELETE"])
def remove_tag(image, tag):
    if image not in imagesList:
        return (f"Sorry, image {image} does not exist!", 404)
    image_tags = get_tags(img_name=image)
    tag = tag.lower().strip()
    if tag not in image_tags:
        return (f"image {image} does not have tag {tag}.", 204)
    cur = get_db().cursor()
    ddl = f"DELETE FROM tags WHERE path = '{image}' AND tag = '{tag}'"
    cur.execute(ddl)
    get_db().commit()
    return ("tag removed", 200)


@app.route("/image/<image>/tags", methods=["DELETE"])
def remove_all_tags(image):
    if image not in imagesList:
        return (f"Sorry, image {image} does not exist!", 404)
    cur = get_db().cursor()
    ddl = f"DELETE FROM tags WHERE path = '{image}'"
    cur.execute(ddl)
    get_db().commit()
    return (f"reset {image} tags", 200)


@app.teardown_appcontext
def close_connection(e):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
