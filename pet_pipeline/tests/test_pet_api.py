from fastapi.testclient import TestClient

from shengsheng_pet_pipeline.main import app

client = TestClient(app)


def test_concept_job_completes_with_stub_url() -> None:
    created = client.post(
        "/v1/pets/jobs",
        json={
            "child_id": "child_test",
            "description": "a gentle blue fox with a scarf",
            "output_mode": "concept_2d",
        },
    )
    assert created.status_code == 202
    job_id = created.json()["job_id"]
    fetched = client.get(f"/v1/pets/jobs/{job_id}")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "completed"
    assert fetched.json()["specification"]["species"] == "fox"


def test_missing_job_uses_standard_error_contract() -> None:
    response = client.get("/v1/pets/jobs/not_found")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "pet_job_not_found"
