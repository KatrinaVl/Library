from fastapi.testclient import TestClient
from ..api import app

client = TestClient(app)


def get_token():
    body = {"email": "elena@gmail.com", "password": "my_very_secret_password"}

    response = client.post("/login", json=body)
    data = response.json()

    return data["token"]


def test_register():

    body = {"email": "elena%@gmail.com", "password": "my_very_secret_password"}

    response = client.post("/register", json=body)

    assert response.status_code == 201


def test_login():

    body = {"email": "elena1@gmail.com", "password": "my_very_secret_password"}

    response = client.post("/login", json=body)

    assert response.status_code == 201
    data = response.json()
    assert data["token"] != ""


def test_register_book():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    body = {
        "title": "Ninth House ___last",
        "author": "Leigh Bardugo",
        "publish_year": 2012,
        "isbn": "sdkjdkjhgcdjjvfbпbw",
        "count": 15,
    }

    response = client.post("/register_book", json=body, headers=headers)

    assert response.status_code == 201
    data = response.json()

    assert data["book"]["id"] != ""
    assert data["book"]["title"] == "Ninth House ___last"
    assert data["book"]["author"] == "Leigh Bardugo"
    assert data["book"]["isbn"] == "sdkjdkjhgcdjjvfbпbw"
    assert data["book"]["count"] == "15"


def test_update_book():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    body = {
        "id": "6d96a932-b606-4e04-8c1d-e9ad067bd6c3",
        "title": "Dune",
        "author": "Frank Herbert",
        "publish_year": 1965,
        "isbn": "sdkjfnbw",
        "count": 35,
    }

    response = client.post("/update_book", json=body, headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["book"]["id"] == "6d96a932-b606-4e04-8c1d-e9ad067bd6c3"
    assert data["book"]["title"] == "Dune"
    assert data["book"]["author"] == "Frank Herbert"
    assert data["book"]["isbn"] == "sdkjfnbw"
    assert data["book"]["count"] == "35"


def test_get_book():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/get_book/6d96a932-b606-4e04-8c1d-e9ad067bd6c3", headers=headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["book"]["id"] == "6d96a932-b606-4e04-8c1d-e9ad067bd6c3"
    assert data["book"]["title"] == "Dune"
    assert data["book"]["author"] == "Frank Herbert"
    assert data["book"]["isbn"] == "sdkjfnbw"
    assert data["book"]["count"] == "35"


def test_delete_book():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(
        "/delete_book/bd85a14e-34c6-42ce-9144-fe6d8d0bbb47", headers=headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "book is deleted"


def test_add_reader():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    body = {"name": "kolya_vk", "email": "kolya_vk@mail.com"}

    response = client.post("/add_reader", json=body, headers=headers)

    assert response.status_code == 201
    data = response.json()

    assert data["message"] == "reader is added"


def test_update_reader():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    body = {"name": "kate", "email": "kate_7@gmail.com"}

    response = client.post(
        "/update_reader/9ff2ebef-7430-4745-8b7d-db6f02183d3d",
        json=body,
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["reader"]["name"] == "kate"
    assert data["reader"]["email"] == "kate_7@gmail.com"


def test_get_reader():
    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/get_reader/9ff2ebef-7430-4745-8b7d-db6f02183d3d", headers=headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["reader"]["name"] == "kate"
    assert data["reader"]["email"] == "kate_7@gmail.com"


def test_delete_reader():
    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(
        "/delete_reader/362a7cbd-030e-42fc-9b5d-2567f6116dd6", headers=headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "reader is deleted"


def test_give_and_return_book():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    body_give = {
        "book_id": "bd85a14e-34c6-42ce-9144-fe6d8d0bbb47",
        "reader_id": "9ff2ebef-7430-4745-8b7d-db6f02183d3d",
    }

    response = client.post("/give_book", json=body_give, headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert (
        data["message"]
        == f"reader {body_give['reader_id']} " +
        f"take the {body_give['book_id']} book"
    )

    borrowed_id = data["borrowed_id"]

    body = {"book_id": "bd85a14e-34c6-42ce-9144-fe6d8d0bbb47",
            "borrow_id": borrowed_id}

    response = client.post("/return_book", json=body, headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert (
        data["message"]
        == f"reader {body_give['reader_id']} return the {body['book_id']} book"
    )


def test_get_books():

    book_info = {"per_page": 2, "page": 1}

    response = client.post("/get_books", json=book_info)

    assert response.status_code == 200
    data = response.json()

    assert len(data["books"]) == 2


def get_books_for_reader():

    token = get_token()

    headers = {"Authorization": f"Bearer {token}"}

    body_book_1 = {
        "book_id": "6bc7f43d-2f4f-459b-8380-5929c16998c2",
        "reader_id": "9ff2ebef-7430-4745-8b7d-db6f02183d3d",
    }

    response = client.post("/give_book", json=body_book_1, headers=headers)

    assert response.status_code == 200
    data = response.json()
    borrowed_id_1 = data["borrowed_id"]

    body_book_2 = {
        "book_id": "893699b9-0962-4c44-924a-0f3f706cf191",
        "reader_id": "9ff2ebef-7430-4745-8b7d-db6f02183d3d",
    }

    response = client.post("/give_book", json=body_book_2, headers=headers)

    assert response.status_code == 200
    data = response.json()
    borrowed_id_2 = data["borrowed_id"]

    book_info = {"per_page": 2, "page": 2}

    response = client.post(
        "/get_books/9ff2ebef-7430-4745-8b7d-db6f02183d3d",
        json=book_info,
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["books"]) == 2

    body_borrowed_1 = {
        "book_id": body_book_1.book_id,
        "borrow_id": borrowed_id_1}

    response = client.post(
        "/return_book", json=body_borrowed_1, headers=headers)

    assert response.status_code == 200

    body_borrowed_2 = {
        "book_id": body_book_2.book_id,
        "borrow_id": borrowed_id_2}

    response = client.post(
        "/return_book", json=body_borrowed_2, headers=headers)

    assert response.status_code == 200
