import io

from fastapi import status

# Fixtures for client, auth_headers, and test_project should be provided by conftest.py


def test_upload_documents(
    client, auth_headers, test_project, ensure_s3_bucket
):
    files = [
        ("files", ("file1.txt", io.BytesIO(b"data1"), "text/plain")),
        ("files", ("file2.txt", io.BytesIO(b"data2"), "text/plain")),
    ]
    response = client.post(
        f"/project/{test_project['id']}/documents",
        files=files,
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert len(data) == 2
    assert data[0]["filename"] == "file1.txt"
    assert data[1]["filename"] == "file2.txt"


def test_upload_documents_over_limit(
    client, auth_headers, test_project, monkeypatch, ensure_s3_bucket
):
    # Patch settings to a very low limit
    monkeypatch.setattr(
        "app.core.config.settings.PROJECT_FILE_SIZE_LIMIT", 1
    )
    files = [
        ("files", ("file1.txt", io.BytesIO(b"data1"), "text/plain")),
    ]
    response = client.post(
        f"/project/{test_project['id']}/documents",
        files=files,
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "file size limit" in response.text


def test_download_document(
    client, auth_headers, test_project, test_document, ensure_s3_bucket
):
    response = client.get(
        f"/document/{test_document['id']}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert (
        response.content == b"data1"
    )  # Assuming test_document content is 'data1'


def test_update_document(
    client, auth_headers, test_project, test_document, ensure_s3_bucket
):
    file = ("file", ("updated.txt", io.BytesIO(b"newdata"), "text/plain"))
    response = client.put(
        f"/document/{test_document['id']}",
        files=[file],
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["filename"] == "updated.txt"


def test_delete_document(
    client, auth_headers, test_project, test_document, ensure_s3_bucket
):
    response = client.delete(
        f"/document/{test_document['id']}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Try to get again
    response = client.get(
        f"/document/{test_document['id']}", headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
