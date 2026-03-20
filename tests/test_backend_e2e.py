import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import uuid
import json
from unittest.mock import patch

from backend.app.main import app
from backend.app.database.mysql import Base, get_db
from backend.app.database import models
from backend.app.workers.celery_worker import process_recovery

# Setup test database (SQLite in-memory for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_investigation():
    response = client.post(
        "/api/investigations",
        params={"case_name": "Test Case 1", "investigator": "John Doe", "description": "Testing E2E"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["case_name"] == "Test Case 1"
    assert "id" in data
    return data["id"]

@patch("backend.app.main.process_recovery.delay")
@patch("backend.app.main.compute_hash.delay")
def test_upload_image_and_recover(mock_compute_hash, mock_process_recovery):
    class MockTask:
        id = "mock-task-id"
    mock_process_recovery.return_value = MockTask()
    
    # 1. Create Investigation
    inv_id = test_create_investigation()

    # 2. Create a dummy file
    dummy_file_path = "dummy_image.dd"
    with open(dummy_file_path, "wb") as f:
        # Create a small dummy file with some repeating patterns
        f.write(b"\xff\xd8\xff\xe0" + b"\x00" * 4090) 
        f.write(b"%PDF-1.4" + b"\x00" * 4090)

    try:
        # 3. Upload Image
        with open(dummy_file_path, "rb") as f:
            response = client.post(
                f"/api/upload-image?investigation_id={inv_id}",
                files={"file": ("dummy_image.dd", f, "application/octet-stream")}
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "uploaded"
        image_id = data["image_id"]

        # 4. Trigger Recovery (Mocked)
        response_recover = client.post(f"/api/recover/{image_id}")
        assert response_recover.status_code == 200
        task_id = response_recover.json()["task_id"]
        assert task_id == "mock-task-id"
        
        # Now run the actual process_recovery task synchronously to test the logic
        result = process_recovery(image_id)
        print("PROCESS RECOVERY RESULT:", result)

        # 5. Check Fragments Endpoint
        response_fragments = client.get(f"/api/fragments/{image_id}")
        assert response_fragments.status_code == 200
        fragments = response_fragments.json()
        assert isinstance(fragments, list)
        assert len(fragments) > 0

        # 6. Check Recovered Files Endpoint
        response_recovered = client.get(f"/api/recovered-files/{image_id}")
        assert response_recovered.status_code == 200
        recovered_files = response_recovered.json()
        assert isinstance(recovered_files, list)
    finally:
        if os.path.exists(dummy_file_path):
            os.remove(dummy_file_path)
