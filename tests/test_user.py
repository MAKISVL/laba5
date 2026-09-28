from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

users = [
    {'id': 1, 'name': 'Ivan Ivanov', 'email': 'i.i.ivanov@mail.com'},
    {'id': 2, 'name': 'Petr Petrov', 'email': 'p.p.petrov@mail.com'},
]


def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]


def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'nonexistent@mail.com'})
    assert response.status_code == 404


def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    response = client.post(
        "/api/v1/user",
        json={"name": "New User", "email": "new.user@mail.com"}
    )
    assert response.status_code == 201
    assert isinstance(response.json(), int)

    get_response = client.get("/api/v1/user", params={'email': 'new.user@mail.com'})
    assert get_response.status_code == 200
    assert get_response.json()['email'] == 'new.user@mail.com'


def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    response = client.post(
        "/api/v1/user",
        json={"name": "Duplicate", "email": users[0]['email']}
    )
    assert response.status_code == 409


def test_delete_user():
    '''Удаление пользователя'''
    client.post(
        "/api/v1/user",
        json={"name": "To Delete", "email": "to.delete@mail.com"}
    )

    response = client.delete("/api/v1/user", params={'email': 'to.delete@mail.com'})
    assert response.status_code == 204

    get_response = client.get("/api/v1/user", params={'email': 'to.delete@mail.com'})
    assert get_response.status_code == 404


def test_get_all_users():
    '''Получение списка всех пользователей'''
    response = client.get("/api/v1/user/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_update_user_name():
    '''Успешное обновление имени пользователя'''
    client.post("/api/v1/user", json={"name": "Before", "email": "upd@mail.com"})
    response = client.patch(
        "/api/v1/user",
        params={'email': 'upd@mail.com'},
        json={"name": "After"}
    )
    assert response.status_code == 200
    assert response.json()['name'] == "After"


def test_update_user_not_found():
    '''Обновление несуществующего пользователя'''
    response = client.patch(
        "/api/v1/user",
        params={'email': 'ghost@mail.com'},
        json={"name": "X"}
    )
    assert response.status_code == 404


def test_update_user_email_conflict():
    '''Обновление email на уже занятый'''
    client.post("/api/v1/user", json={"name": "A", "email": "a@mail.com"})
    client.post("/api/v1/user", json={"name": "B", "email": "b@mail.com"})
    response = client.patch(
        "/api/v1/user",
        params={'email': 'b@mail.com'},
        json={"email": "a@mail.com"}
    )
    assert response.status_code == 409
