from flask import Blueprint, request, jsonify
from src.extensions import db
from src.models import Student


def create_blueprint(name, version=None):
    bp = Blueprint(name, __name__)

    def wrap(s: Student):
        data = s.to_dict()
        if version:
            data["version"] = version
        return data

    @bp.post("/")
    def create():
        d = request.get_json() or {}
        try:
            age = int(d.get("age"))
        except Exception:
            return {"error": "age must be integer"}, 400

        if age < 0:
            return {"error": "age must be >= 0"}, 400

        s = Student(name=d.get("name"), age=age, course=d.get("course"))
        db.session.add(s)
        db.session.commit()
        return wrap(s), 201

    @bp.get("/")
    def list_students():
        return jsonify([wrap(s) for s in Student.query.all()])

    @bp.get("/<int:id>")
    def get_one(id):
        s = Student.query.get(id)
        if not s:
            return {"error": "Not found"}, 404
        return wrap(s)

    @bp.put("/<int:id>")
    def replace(id):
        s = Student.query.get(id)
        if not s:
            return {"error": "Not found"}, 404

        d = request.get_json() or {}
        s.name = d.get("name")
        s.age = int(d.get("age"))
        s.course = d.get("course")
        db.session.commit()
        return wrap(s)

    @bp.patch("/<int:id>")
    def modify(id):
        s = Student.query.get(id)
        if not s:
            return {"error": "Not found"}, 404

        d = request.get_json() or {}
        if "name" in d:
            s.name = d["name"]
        if "age" in d:
            s.age = int(d["age"])
        if "course" in d:
            s.course = d["course"]
        db.session.commit()
        return wrap(s)

    @bp.delete("/<int:id>")
    def delete(id):
        s = Student.query.get(id)
        if not s:
            return {"error": "Not found"}, 404
        db.session.delete(s)
        db.session.commit()
        return "", 204

    return bp


# Create blueprints
students_v1 = create_blueprint("students_v1")
students_v2 = create_blueprint("students_v2", version="v2")
students_legacy = create_blueprint("students_legacy")   # old /students/ route
