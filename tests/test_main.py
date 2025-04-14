import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def mock_db(monkeypatch):
    class MockMySQLDataAccess:
        def execute_non_query(self, query, params):
            pass

        def execute_query(self, query):
            if "SELECT" in query:
                return [
                    {"id": 1, "team_name": "TeamA", "player1": "Player1", "player2": "Player2"},
                    {"id": 2, "team_name": "TeamB", "player1": "Player3", "player2": "Player4"},
                ]
            return []

    monkeypatch.setattr("main.db", MockMySQLDataAccess())

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_add_team_success(mock_db):
    response = client.post("/teams/TeamC/Player5/Player6")
    assert response.status_code == 201
    assert response.json() == {"message": "Team added successfully."}

def test_add_team_empty_player(mock_db):
    response = client.post("/teams/TeamC//Player6")
    assert response.status_code == 400
    assert response.json() == {"detail": "Player names cannot be empty."}

def test_add_team_duplicate_name(mock_db):
    client.post("/teams/TeamA/Player1/Player2")  # Mock existing team
    response = client.post("/teams/TeamA/Player7/Player8")
    assert response.status_code == 400
    assert response.json() == {"detail": "Team already exists with this name."}

def test_get_all_teams(mock_db):
    response = client.get("/teams")
    assert response.status_code == 200
    assert response.json() == {
        "teams": [
            {"team_id": 1, "team_name": "TeamA", "player1": "Player1", "player2": "Player2"},
            {"team_id": 2, "team_name": "TeamB", "player1": "Player3", "player2": "Player4"},
        ]
    }

def test_delete_team_success(mock_db):
    client.get("/teams")  # Populate team_list
    response = client.delete("/teams/1")
    assert response.status_code == 204

def test_delete_team_not_found(mock_db):
    response = client.delete("/teams/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found."}