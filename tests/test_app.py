import os
import json
import pytest
from flask import current_app
from website import create_app, db
from website.models import Message, Chat


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def test_home_get(client):
    """Loading the home page with input textarea."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Ask your question..." in response.data


def test_home_post(client):
    response = client.post(
        "/", data={"user_message": "What is the capital of Germany!"}
    )
    decoded_response = response.data.decode()
    response_data = json.loads(decoded_response)
    assert response.status_code == 200
    assert "usr_msg" in response_data and "ai_msg" in response_data
    assert len(response_data["usr_msg"]) > 0
    assert len(response_data["ai_msg"]) > 0
    assert "berlin" in response_data["ai_msg"].lower()


def test_clear_chat(client):
    from website.models import Chat, Message

    response = client.post("/", data={"user_message": "Hello!"})
    assert Chat.query.count() == 1  # 1 chat
    assert Message.query.count() == 2  # 2 messages per interaction (usr, ai)

    response = client.post("/reset_chat")
    assert response.status_code == 200
    assert response.json["status"] == "success"

    assert Chat.query.count() == 0
    assert Message.query.count() == 0


def test_error_404(client):
    """Test error 404."""
    request = client.get("/this-does-not-exist")
    assert request.status_code == 404


def test_concurrent_requests(client):
    """Testing if the chatbot handles multiple concurrent requests."""
    from threading import Thread

    def post_message():
        client.post("/", data={"user_message": "Hello!"})

    threads = [Thread(target=post_message) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert Message.query.count() == 20  # 10 user messages + 10 AI messages


def test_form_validation_upper_bound(client):
    """Upper bound error test for allowed number of characters."""
    response = client.post(
        "/", data={"user_message": "A" * 4001}
    )  # Exceeding the maxlength
    assert response.status_code == 200
    assert b"Input is too long!" in response.data


def test_form_validation_lower_bound(client):
    """Lower bound error test for allowed number of characters."""
    response = client.post("/", data={"user_message": ""})  # Empty message
    assert response.status_code == 200
    assert b"Empty message!" in response.data


def test_invalid_data(client):
    """Testing the backend with invalid input data."""
    response = client.post("/", data={"user_message": None})
    assert response.status_code == 200
    assert b"Invalid input provided!" in response.data

    response = client.post("/", data={})
    assert response.status_code == 200
    assert b"Invalid input provided!" in response.data
