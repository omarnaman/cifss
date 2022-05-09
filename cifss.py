#!/usr/bin/env python3

from flask import Flask, request, abort, Response
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256
from magic import Magic
from mimetypes import guess_extension
from pathlib import Path
import json


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

    def json(self)-> str:
        res = {
            "id": self.id,
            "ext": self.extension,
            "mime": self.mime_type,
            "digest": self.digest 
        }
        return json.dumps(res)

    def __init__(self, digest, extension, mime_type) -> None:
        self.digest = digest
        self.extension = extension
        self.mime_type = mime_type

    def store(fs):
        data = fs.stream.read()
        digest = sha256(data).hexdigest()
        mime_type = mime_magic.from_buffer(data)
        extension = guess_extension(mime_type)

        storage_path = Path(STORAGE_PATH)
        storage_path.mkdir(parents=True, exist_ok=True)
        file_path = storage_path / digest
        if file_path.is_file():
            file = File.get_by_digest(digest)
            assert(file is not None)
            return str(file.id)

        with open(file_path, 'wb') as f:
            f.write(data)
        file = File(digest, extension, mime_type)
        db.session.add(file)
        db.session.commit()
        
        return str(file.id)

    def read(self):
        file_path = Path(STORAGE_PATH) / self.digest
        with open(file_path, 'rb') as f:
            return f.read()

    def get_by_digest(digest):
        file = db.session.query(File).filter_by(digest=digest).first()
        
        return file

    @classmethod
    def get(cls, id):
        file: File = cls.query.get(id)
        return file


    @classmethod
    def print(cls, id):
        file: File = cls.query.get(id)
        return file.json()

db.create_all()

@app.route("/", methods=["POST"])
def store():
    if request.method == "POST":
        if len(request.files) > 0:
            return File.store(request.files[""])

        abort(400)

@app.route("/<id>", methods=["GET"])
def get(id):
    if request.method == "GET":
        file = File.get(id)
        if file is None:
            abort(404)
        res = Response(response=file.read(), mimetype=file.mime_type)
        return res

@app.route("/print/<id>", methods=["GET"])
def print_file(id):
    if request.method == "GET":
        return File.print(id)
    abort(400)

if __name__=="__main__":
    app.run(debug=True, port="5000", host="0.0.0.0",)