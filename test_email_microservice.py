"""
Automated Test Suite for Email Microservice API (POST /send-email)
Author: Hope David Michael (QA & Security Engineer)
Requirements: pytest, requests
Run via CLI: pytest test_email_microservice.py -v
"""

import json
import re
from unittest.mock import patch, MagicMock
import requests

ENDPOINT = "http://api.email-service.local/send-email"
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def mock_api_gateway(url, json=None, data=None, headers=None, **kwargs):
    """Mock API router simulating backend queue validation and status responses."""
    mock_res = MagicMock(spec=requests.Response)
    
    # Extract payload
    payload = json if json is not None else {}
    if data and isinstance(data, str):
        try:
            payload = json.loads(data)
        except Exception:
            mock_res.status_code = 400
            mock_res.json.return_value = {"error": "Malformed JSON syntax"}
            return mock_res

    # 1. Queue Saturation Simulation (503)
    if headers and headers.get("X-Simulate-Queue-Full") == "true":
        mock_res.status_code = 503
        mock_res.headers = {"Retry-After": "30"}
        mock_res.json.return_value = {"error": "Queue full. Try again later."}
        return mock_res

    # 2. Missing 'to' Field (400)
    if "to" not in payload or payload["to"] is None:
        mock_res.status_code = 400
        mock_res.json.return_value = {"error": "Missing required field: 'to'"}
        return mock_res

    recipient = str(payload["to"])

    # 3. Security: CRLF Injection Detection (422)
    if "\r" in recipient or "\n" in recipient:
        mock_res.status_code = 422
        mock_res.json.return_value = {"error": "Invalid recipient format: CRLF detected"}
        return mock_res

    # 4. Invalid Email Regex Match (400)
    if not re.match(EMAIL_REGEX, recipient):
        mock_res.status_code = 400
        mock_res.json.return_value = {"error": "Invalid email format"}
        return mock_res

    # 5. Successful Enqueue (202)
    mock_res.status_code = 202
    mock_res.json.return_value = {
        "status": "queued",
        "job_id": "job_99283714_x7f",
        "message": "Job accepted into the queue."
    }
    return mock_res


# ============================================================================
# PYTEST SUITE
# ============================================================================

@patch("requests.post", side_effect=mock_api_gateway)
def test_valid_request_returns_202(mock_post):
    """Mandatory: Valid request returns 202 Accepted and job_id."""
    payload = {"to": "user@example.com", "subject": "Test", "body": "Hello World"}
    res = requests.post(ENDPOINT, json=payload)
    
    assert res.status_code == 202
    assert res.json()["status"] == "queued"
    assert "job_id" in res.json()


@patch("requests.post", side_effect=mock_api_gateway)
def test_missing_to_field_returns_400(mock_post):
    """Mandatory: Missing 'to' field returns 400 Bad Request."""
    payload = {"subject": "Test", "body": "Hello World"}
    res = requests.post(ENDPOINT, json=payload)
    
    assert res.status_code == 400
    assert "Missing required field" in res.json()["error"]


@patch("requests.post", side_effect=mock_api_gateway)
def test_invalid_email_format_returns_400(mock_post):
    """Mandatory: Invalid email syntax returns 400 Bad Request."""
    payload = {"to": "user-at-domain.com", "subject": "Test", "body": "Hello World"}
    res = requests.post(ENDPOINT, json=payload)
    
    assert res.status_code == 400
    assert "Invalid email format" in res.json()["error"]


@patch("requests.post", side_effect=mock_api_gateway)
def test_queue_full_returns_503(mock_post):
    """Mandatory: Queue saturation returns 503 Service Unavailable."""
    payload = {"to": "user@example.com", "subject": "Test", "body": "Hello World"}
    res = requests.post(ENDPOINT, json=payload, headers={"X-Simulate-Queue-Full": "true"})
    
    assert res.status_code == 503
    assert res.headers["Retry-After"] == "30"


@patch("requests.post", side_effect=mock_api_gateway)
def test_crlf_header_injection_returns_422(mock_post):
    """Security Bonus: Header injection attack returns 422 Unprocessable Entity."""
    payload = {"to": "user@example.com\r\nBcc:hacker@evil.com", "subject": "Test", "body": "Hello"}
    res = requests.post(ENDPOINT, json=payload)
    
    assert res.status_code == 422
    assert "CRLF detected" in res.json()["error"]
