#!/usr/bin/env python3

from flask import Flask, request, abort, Response
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256
from magic import Magic
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
    name = db.Column(db.String)
    digest = db.Column(db.String, unique = True)
    mime_type = db.Column(db.String)

    def __repr__(self) -> str:
        return self.json()

    def json(self)-> str:
        res = {
            "id": self.id,
            "name": self.name,
            "mime": self.mime_type,
            "digest": self.digest
        }
        return json.dumps(res)

    def __init__(self, name, digest, mime_type) -> None:
        self.name = name
        self.digest = digest
        self.mime_type = mime_type

    def store(name, fs):
        data = fs.stream.read()
        digest = sha256(data).hexdigest()

        storage_path = Path(STORAGE_PATH)
        storage_path.mkdir(parents=True, exist_ok=True)
        file_path = storage_path / digest
        if file_path.is_file():
            file = File.get_by_digest(digest)
            assert(file is not None)
            return str(file.id)

        with open(file_path, 'wb') as f:
            f.write(data)
            mime_type = mime_magic.from_file(file_path)
        file = File(name, digest, mime_type)
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
        if file:
            return file.json()
        else:
            return None

db.create_all()

@app.route("/", methods=["POST"])
def store():
    if request.method == "POST":
        if len(request.files) > 0:
            filename = list(request.files.keys())[0]
            return File.store(filename, request.files[filename])

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
        res = File.print(id)
        if res:
            return res, 200
        else:
            return "", 404 
    abort(400)

if __name__=="__main__":
    app.run(debug=True, port="5000", host="0.0.0.0",)