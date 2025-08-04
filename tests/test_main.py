import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app

client = TestClient(app)


@patch("src.main.ImageAnalyzer.analyze_image")
def test_analyze_image_endpoint(mock_analyze):
    mock_analyze.return_value = "Mocked analysis"
    with open("tests/test.png", "rb") as f:
        response = client.post(
            "/analyze-image", files={"file": ("test.png", f, "image/png")}
        )
    assert response.status_code == 200
    assert "image_description" in response.json()


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Optimeleon Landing Page Generator API is up."
    }


def test_generate_content_missing_fields():
    payload = {
        "image_description": "A fast shoe ad",
        "original_headline": "<h1>Run Fast</h1>",
    }
    response = client.post("/generate-content", json=payload)
    assert response.status_code == 422  # validation error
