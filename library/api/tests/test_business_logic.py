from fastapi.testclient import TestClient
from ..api import app

client = TestClient(app)


def get_token():
    body = {"email": "elena@gmail.com", "password": "my_very_secret_password"}

    response = client.post("/login", json=body)
    data = response.json()

    return data["token"]


def test_take_ended_book():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    """ first person take the Kolobock """
    body_give_1 = {
        "book_id": "2a9e86f3-06b0-47a8-9b4e-77225ef7c405",
        "reader_id": "9ff2ebef-7430-4745-8b7d-db6f02183d3d",
    }

    response = client.post("/give_book", json=body_give_1, headers=headers)

    assert response.status_code == 200
    data = response.json()
    borrowed_id = data["borrowed_id"]

    assert (
        data["message"]
        == f"reader {body_give_1['reader_id']} take "
        + f"the {body_give_1['book_id']} book"
    )

    """ second person try to take the Kolobock """
    body_give_2 = {
        "book_id": "2a9e86f3-06b0-47a8-9b4e-77225ef7c405",
        "reader_id": "b4254b90-be28-4c8c-abb9-d8bc29a3f39b",
    }

    response = client.post("/give_book", json=body_give_2, headers=headers)

    assert response.status_code == 404
    data = response.json()

    assert data["message"] == "There is no any book"

    """ first person return the Kolobock """
    body = {"book_id": "2a9e86f3-06b0-47a8-9b4e-77225ef7c405",
            "borrow_id": borrowed_id}

    response = client.post("/return_book", json=body, headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert (
        data["message"]
        == f"reader {body_give_1['reader_id']} " +
        f"return the {body['book_id']} book"
    )


def test_take_more_than_4_books():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    """ take 3 books """

    body_give_1 = {
        "book_id": "9acf5987-9b3d-4160-9794-1e6c64bdc60c",
        "reader_id": "9ff2ebef-7430-4745-8b7d-db6f02183d3d",
    }

    response = client.post("/give_book", json=body_give_1, headers=headers)

    assert response.status_code == 200
    data = response.json()
    borrowed_id_1 = data["borrowed_id"]

    body_give_2 = {
        "book_id": "6d96a932-b606-4e04-8c1d-e9ad067bd6c3",
        "reader_id": "9ff2ebef-7430-4745-8b7d-db6f02183d3d",
    }

    response = client.post("/give_book", json=body_give_2, headers=headers)

    assert response.status_code == 200
    data = response.json()
    borrowed_id_2 = data["borrowed_id"]

    body_give_3 = {
        "book_id": "747a91f0-6a02-468e-9de6-44f39b632d7f",
        "reader_id": "9ff2ebef-7430-4745-8b7d-db6f02183d3d",
    }

    response = client.post("/give_book", json=body_give_3, headers=headers)

    assert response.status_code == 200
    data = response.json()
    borrowed_id_3 = data["borrowed_id"]

    """ take 4th book """

    body_give_4 = {
        "book_id": "f871c6c2-6002-4587-9896-96fd0cdd8a15",
        "reader_id": "9ff2ebef-7430-4745-8b7d-db6f02183d3d",
    }

    response = client.post("/give_book", json=body_give_4, headers=headers)

    assert response.status_code == 409
    data = response.json()

    assert data["message"] == "Too many book has already taken"

    """ return books """

    body_1 = {"book_id": body_give_1["book_id"], "borrow_id": borrowed_id_1}

    response = client.post("/return_book", json=body_1, headers=headers)

    assert response.status_code == 200

    body_2 = {"book_id": body_give_2["book_id"], "borrow_id": borrowed_id_2}

    response = client.post("/return_book", json=body_2, headers=headers)

    assert response.status_code == 200

    body_3 = {"book_id": body_give_3["book_id"], "borrow_id": borrowed_id_3}

    response = client.post("/return_book", json=body_3, headers=headers)

    assert response.status_code == 200


def test_return_wrong_book():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    body_give_1 = {
        "book_id": "9acf5987-9b3d-4160-9794-1e6c64bdc60c",
        "reader_id": "9ff2ebef-7430-4745-8b7d-db6f02183d3d",
    }

    response = client.post("/give_book", json=body_give_1, headers=headers)

    assert response.status_code == 200
    data = response.json()
    borrowed_id_1 = data["borrowed_id"]

    body_1 = {
        "book_id": "747a91f0-6a02-468e-9de6-44f39b632d7f",
        "borrow_id": borrowed_id_1,
    }

    response = client.post("/return_book", json=body_1, headers=headers)

    assert response.status_code == 409
    data = response.json()
    assert data["message"] == "Wrong book was returned"

    body_1 = {"book_id": body_give_1["book_id"], "borrow_id": borrowed_id_1}

    response = client.post("/return_book", json=body_1, headers=headers)

    assert response.status_code == 200


def test_return_returned_book():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    body_give_1 = {
        "book_id": "9acf5987-9b3d-4160-9794-1e6c64bdc60c",
        "reader_id": "9ff2ebef-7430-4745-8b7d-db6f02183d3d",
    }

    response = client.post("/give_book", json=body_give_1, headers=headers)

    assert response.status_code == 200
    data = response.json()
    borrowed_id_1 = data["borrowed_id"]

    body_1 = {"book_id": body_give_1["book_id"], "borrow_id": borrowed_id_1}

    response = client.post("/return_book", json=body_1, headers=headers)

    assert response.status_code == 200

    response = client.post("/return_book", json=body_1, headers=headers)

    assert response.status_code == 409
    data = response.json()
    assert data["message"] == "Book has already returned"


def test_action_without_jwt():

    response = client.get("/get_book/6d96a932-b606-4e04-8c1d-e9ad067bd6c3")

    assert response.status_code == 401


def test_action_with_jwt():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/get_book/6d96a932-b606-4e04-8c1d-e9ad067bd6c3", headers=headers
    )

    assert response.status_code == 200
    data = response.json()
