#!/usr/bin/env python3

from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256
from magic import Magic
from mimetypes import guess_extension
from pathlib import Path


STORAGE_PATH = "filestorage"

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

mime_magic = Magic(mime=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    digest = db.Column(db.String, unique = True)
    extension = db.Column(db.UnicodeText)
    mime_type = db.Column(db.UnicodeText)

    def __repr__(self) -> str:
        return f"{self.id}:\n\text: {self.extension}\n\tmime: {self.mime_type}"

    def __init__(self, digest, extension, mime_type) -> None:
        self.digest = digest
        self.extension = extension
        self.mime_type = mime_type

    def store(fs):
        data = fs.stream.read()
        digest = sha256(data).hexdigest()
        mime_type = mime_magic.from_buffer(data)
        extension = guess_extension(mime_type)
        file = File(digest, extension, mime_type)

        storage_path = Path(STORAGE_PATH)
        storage_path.mkdir(parents=True, exist_ok=True)
        with open(storage_path / digest, 'wb') as f:
            f.write(data)
        db.session.add(file)
        db.session.commit()
        
        return str(file.id)

    @classmethod
    def get(cls, id):
        file: File = cls.query.get(id)
        file_path = Path(STORAGE_PATH) / file.digest
        with open(file_path, 'rb') as f:
            return f.read()

    @classmethod
    def print(cls, id):
        file: File = cls.query.get(id)
        print(file)

db.create_all()

@app.route("/", methods=["POST"])
def store():
    if request.method == "POST":
        print(request.files)
        if len(request.files) > 0:
            return File.store(request.files[""])

        abort(400)

@app.route("/<id>", methods=["GET"])
def get(id):
    if request.method == "GET":
        return File.get(id)

@app.route("/print/<id>", methods=["POST"])
def print_file(id):
    if request.method == "POST":
        File.print(id)
        return "OK"
    abort(400)

if __name__=="__main__":
    app.run(debug=True, port="5000", host="0.0.0.0",)