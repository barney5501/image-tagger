from flask import Flask, render_template, jsonify
import os

imagesPath = "static/images"
imagesList = os.listdir(imagesPath)
imagesList = [img for img in imagesList if not img.endswith(".txt")]
imageIndex = 0


app = Flask(__name__)


@app.route("/")
def main():
    return "Image Tagger!"


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
