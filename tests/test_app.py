
import pytest
import app as url_shortener


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Use a separate temporary database for each test.
    test_database = tmp_path / "test_urls.db"

    monkeypatch.setattr(
        url_shortener,
        "DATABASE",
        test_database
    )

    url_shortener.init_db()

    with url_shortener.app.test_client() as test_client:
        yield test_client


def test_create_short_url(client):
    original_url = "https://example.com/articles/python"

    response = client.post(
        "/api/urls",
        json={"url": original_url}
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["original_url"] == original_url
    assert data["short_code"]
    assert data["short_url"].endswith(
        "/" + data["short_code"]
    )


def test_reject_invalid_url(client):
    response = client.post(
        "/api/urls",
        json={"url": "javascript:alert(1)"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Enter a valid HTTP or HTTPS URL."
    )


def test_redirect_to_original_url(client):
    original_url = "https://example.com/articles/python"

    create_response = client.post(
        "/api/urls",
        json={"url": original_url}
    )

    short_code = create_response.get_json()["short_code"]

    response = client.get(
        f"/{short_code}",
        follow_redirects=False
    )

    assert response.status_code == 302
    assert response.headers["Location"] == original_url


def test_unknown_short_code_returns_404(client):
    response = client.get("/codigoInexistente")

    assert response.status_code == 404
    assert response.get_json()["error"] == (
        "Short URL not found."
    )
