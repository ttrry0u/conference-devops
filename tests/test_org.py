from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def _create_participant():
    return client.post(
        "/participants/",
        json={
            "full_name": "Тест",
            "email": "org@example.com",
            "role": "attendee",
            "is_online": False,
        },
    ).json()


def test_create_fee():
    p = _create_participant()
    response = client.post(
        "/org/fees/", json={"participant_id": p["id"], "amount": 5000}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "unpaid"


def test_pay_fee():
    p = _create_participant()
    fee = client.post(
        "/org/fees/", json={"participant_id": p["id"], "amount": 5000}
    ).json()

    response = client.patch(f"/org/fees/{fee['id']}/pay")
    assert response.status_code == 200
    assert response.json()["status"] == "paid"


def test_book_hotel_without_payment():
    # БИЗНЕС-ПРАВИЛО: бронирование без оплаты должно возвращать 400.
    p = _create_participant()
    hotel = client.post(
        "/org/hotels/",
        json={
            "participant_id": p["id"],
            "check_in": "2026-12-12",
            "check_out": "2026-12-13",
        },
    ).json()

    response = client.patch(f"/org/hotels/{hotel['id']}/book")
    assert response.status_code == 400


def test_book_hotel_with_payment():
    p = _create_participant()
    fee = client.post(
        "/org/fees/", json={"participant_id": p["id"], "amount": 5000}
    ).json()
    client.patch(f"/org/fees/{fee['id']}/pay")

    hotel = client.post(
        "/org/hotels/",
        json={
            "participant_id": p["id"],
            "check_in": "2026-12-12",
            "check_out": "2026-12-14",
        },
    ).json()

    response = client.patch(f"/org/hotels/{hotel['id']}/book")
    assert response.status_code == 200
    assert response.json()["status"] == "booked"
