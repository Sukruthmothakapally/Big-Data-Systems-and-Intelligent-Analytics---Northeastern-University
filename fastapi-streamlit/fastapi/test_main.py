from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_tokenize_invalid_service():
    response = client.post(
        url="/api/v1/tokenize",
        json={
            "service": "bardv2",
            "apikey": "generatedapikeytoken",
            "content": ["This is an example sentence"]
        }
    )
    assert response.status_code == 404
    message = response.json()["detail"]
    assert message == "Service not among 'huggingface', 'openai', 'cohere'"


def test_tokenize_invalid_content():
    response = client.post(
        url="/api/v1/tokenize",
        json={
            "service": "huggingface",
            "apikey": "generatedapikeytoken",
            "content": []
        }
    )
    assert response.status_code == 404
    message = response.json()["detail"]
    assert message == "Content should be a list of one or more than items"


def test_tokenize_validinputs():
    response = client.post(
        url="/api/v1/tokenize",
        json={
            "service": "huggingface",
            "apikey": "generatedapikeytoken",
            "content": ["This is an example sentence"]
        }
    )
    assert response.status_code == 200
    print(response.json())
    message = response.json()["embeddings"]
    assert len(message) == 1
'''
def test_tokenize_validapi():
    response = client.post(
        url="/api/v1/tokenize",
        json={
            "service": "openai",
            "apikey": "",
            "content": ["This is an example sentence"]
        }
    )
    assert response.status_code == 404
    message = response.json()["detail"]
    assert message == "api key is required"
    '''