"""
CRUD and validation tests for the /students endpoints.
"""

# ---------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------
def test_create_student_success(client, sample_student):
    response = client.post("/students", json=sample_student)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "T001"
    assert data["name"] == "Test Student"
    assert data["email"] == "test.student@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_student_duplicate_student_id(client, sample_student):
    client.post("/students", json=sample_student)
    # Same student_id, different email
    dup = dict(sample_student)
    dup["email"] = "different@example.com"
    response = client.post("/students", json=dup)
    assert response.status_code == 409
    assert "student_id" in response.json()["detail"]


def test_create_student_duplicate_email(client, sample_student):
    client.post("/students", json=sample_student)
    dup = dict(sample_student)
    dup["student_id"] = "T002"
    response = client.post("/students", json=dup)
    assert response.status_code == 409
    assert "email" in response.json()["detail"]


def test_create_student_invalid_email(client, sample_student):
    bad = dict(sample_student)
    bad["email"] = "not-an-email"
    response = client.post("/students", json=bad)
    assert response.status_code == 422


def test_create_student_cgpa_too_high(client, sample_student):
    bad = dict(sample_student)
    bad["cgpa"] = 15.0
    response = client.post("/students", json=bad)
    assert response.status_code == 422


def test_create_student_cgpa_negative(client, sample_student):
    bad = dict(sample_student)
    bad["cgpa"] = -1.0
    response = client.post("/students", json=bad)
    assert response.status_code == 422


def test_create_student_year_out_of_range(client, sample_student):
    bad = dict(sample_student)
    bad["year"] = 5
    response = client.post("/students", json=bad)
    assert response.status_code == 422


def test_create_student_missing_fields(client):
    response = client.post("/students", json={"name": "Only Name"})
    assert response.status_code == 422


# ---------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------
def test_list_students_empty(client):
    response = client.get("/students")
    assert response.status_code == 200
    assert response.json() == []


def test_list_students(client, sample_student):
    client.post("/students", json=sample_student)
    response = client.get("/students")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_student_by_id_success(client, sample_student):
    created = client.post("/students", json=sample_student).json()
    response = client.get(f"/students/{created['id']}")
    assert response.status_code == 200
    assert response.json()["student_id"] == "T001"


def test_get_student_not_found(client):
    response = client.get("/students/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ---------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------
def test_update_student_success(client, sample_student):
    created = client.post("/students", json=sample_student).json()
    response = client.put(
        f"/students/{created['id']}",
        json={"cgpa": 9.5, "year": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cgpa"] == 9.5
    assert data["year"] == 3
    assert data["name"] == "Test Student"  # unchanged


def test_update_student_not_found(client):
    response = client.put("/students/999999", json={"cgpa": 9.5})
    assert response.status_code == 404


def test_update_student_duplicate_email(client, sample_student):
    s1 = client.post("/students", json=sample_student).json()
    s2_payload = dict(sample_student)
    s2_payload["student_id"] = "T002"
    s2_payload["email"] = "second@example.com"
    s2 = client.post("/students", json=s2_payload).json()

    # Try to give s2 the email of s1
    response = client.put(
        f"/students/{s2['id']}",
        json={"email": s1["email"]},
    )
    assert response.status_code == 409


def test_update_student_invalid_cgpa(client, sample_student):
    created = client.post("/students", json=sample_student).json()
    response = client.put(f"/students/{created['id']}", json={"cgpa": 20.0})
    assert response.status_code == 422


# ---------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------
def test_delete_student_success(client, sample_student):
    created = client.post("/students", json=sample_student).json()
    response = client.delete(f"/students/{created['id']}")
    assert response.status_code == 204

    # Confirm it's gone
    check = client.get(f"/students/{created['id']}")
    assert check.status_code == 404


def test_delete_student_not_found(client):
    response = client.delete("/students/999999")
    assert response.status_code == 404