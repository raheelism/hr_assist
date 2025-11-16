import pytest
import json
from unittest.mock import patch

# Add the backend directory to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login(client):
    # Test successful login
    response = client.post('/login', auth=('testuser', 'password'))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data

    # Test failed login
    response = client.post('/login', auth=('wronguser', 'wrongpassword'))
    assert response.status_code == 401

@patch('agent.HRAssistAgent.chat')
def test_chat(mock_chat, client):
    mock_chat.return_value = "Hello, how can I help you?"

    # Get a token
    response = client.post('/login', auth=('testuser', 'password'))
    token = json.loads(response.data)['token']

    # Test chat with token
    response = client.post('/chat', headers={'x-access-token': token}, json={'message': 'hello'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['response'] == "Hello, how can I help you?"

    # Test chat without token
    response = client.post('/chat', json={'message': 'hello'})
    assert response.status_code == 401
