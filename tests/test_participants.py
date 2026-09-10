from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_participant():
    """Тест создания участника."""
    response = client.post(
        "/participants/",
        json={
            "full_name": "Иванов Иван",
            "email": "test@example.com",
            "role": "speaker",
            "is_online": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Иванов Иван"
    assert "id" in data


def test_get_participants():
    """Тест получения списка участников."""
    response = client.get("/participants/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_duplicate_email():
    """Тест проверки уникальности email."""
    client.post(
        "/participants/",
        json={
            "full_name": "Петров",
            "email": "dup@example.com",
            "role": "attendee",
            "is_online": False,
        },
    )

    response = client.post(
        "/participants/",
        json={
            "full_name": "Сидоров",
            "email": "dup@example.com",
            "role": "attendee",
            "is_online": False,
        },
    )
    assert response.status_code == 400
