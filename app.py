from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["UPLOAD_FOLDER"] = "uploads"
db = SQLAlchemy(app)

class Data(db.Model):
    id = db.Column(db.String, primary_key=True)
    content_type = db.Column(db.String)
    content = db.Column(db.LargeBinary)

db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    user_id = request.form.get("user_id")
    file = request.files.get("file")
    text = request.form.get("text")

    if file:
        filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
        secure_filename(filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        content_type = "file"
        content = filename.encode()
    elif text:
        content_type = "text"
        content = text.encode()
    else:
        return jsonify({"error": "No input provided"}), 400

    data = Data(id=user_id, content_type=content_type, content=content)
    db.session.add(data)
    db.session.commit()

    return jsonify({"success": True, "user_id": user_id})

@app.route("/get_data/<user_id>", methods=["GET"])
def get_data(user_id):
    data = Data.query.get(user_id)
    if data:
        if data.content_type == "text":
            return jsonify({"content_type": "text", "content": data.content.decode()})
        else:
            return send_from_directory(app.config["UPLOAD_FOLDER"], data.content.decode())
    else:
        return jsonify({"error": "Data not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
