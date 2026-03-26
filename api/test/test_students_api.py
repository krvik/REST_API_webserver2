import pytest
from api.src.app import create_app
from api.src.extensions import db


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


# ---------------------------------------
# TEST: Health Check Endpoint
# ---------------------------------------
def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


# ---------------------------------------
# TEST: Create Student (POST /students/)
# ---------------------------------------
def test_create_student(client):
    body = {"name": "John", "age": 20, "course": "Math"}
    res = client.post("/students/", json=body)
    assert res.status_code == 201
    data = res.get_json()
    assert data["name"] == "John"
    assert data["course"] == "Math"


# ---------------------------------------
# TEST: Get All Students (GET /students/)
# ---------------------------------------
def test_list_students(client):
    client.post(
        "/students/",
        json={"name": "A", "age": 21, "course": "CS"}
    )
    client.post(
        "/students/",
        json={"name": "B", "age": 22, "course": "IT"}
    )

    res = client.get("/students/")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 2


# ---------------------------------------
# TEST: Get Student by ID (GET /students/<id>)
# ---------------------------------------
def test_get_student(client):
    created = client.post(
        "/students/",
        json={"name": "Jane", "age": 19, "course": "EE"}
    ).get_json()

    sid = created["id"]

    res = client.get(f"/students/{sid}")
    assert res.status_code == 200
    assert res.get_json()["name"] == "Jane"


# ---------------------------------------
# TEST: Update Student (PUT /students/<id>)
# ---------------------------------------
def test_update_student(client):
    created = client.post(
        "/students/",
        json={"name": "Old", "age": 30, "course": "Bio"}
    ).get_json()

    sid = created["id"]

    update_body = {
        "name": "New",
        "age": 25,
        "course": "AI"
    }

    res = client.put(
        f"/students/{sid}",
        json=update_body
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == "New"
    assert data["age"] == 25


# ---------------------------------------
# TEST: Partial Update (PATCH /students/<id>)
# ---------------------------------------
def test_patch_student(client):
    created = client.post(
        "/students/",
        json={"name": "Patch", "age": 23, "course": "EE"}
    ).get_json()

    sid = created["id"]

    res = client.patch(
        f"/students/{sid}",
        json={"age": 24}
    )

    assert res.status_code == 200
    assert res.get_json()["age"] == 24


# ---------------------------------------
# TEST: Delete Student (DELETE /students/<id>)
# ---------------------------------------
def test_delete_student(client):
    created = client.post(
        "/students/",
        json={"name": "Del", "age": 28, "course": "CE"}
    ).get_json()

    sid = created["id"]

    res = client.delete(f"/students/{sid}")
    assert res.status_code == 204

    # Verify deleted
    res = client.get(f"/students/{sid}")
    assert res.status_code == 404
