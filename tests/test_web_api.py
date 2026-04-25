"""
Smoke tests pentru API-ul FastAPI folosit de UI-ul web.
"""

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from src.simulation_service import SimulationConfig
from web.backend import app as app_module
from web.backend.job_store import JobStore, TrainingJob


def _sample_environment():
    return {
        "id": "test_web_map",
        "name": "Test web map",
        "rows": 5,
        "cols": 5,
        "start": [0, 0],
        "target": [4, 4],
        "grid": [
            [6, 0, 0, 0, 0],
            [1, 1, 0, 1, 0],
            [0, 0, 0, 1, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 0, 1, 5],
        ],
    }


def test_environment_validate_save_and_list():
    client = TestClient(app_module.app)
    environment = _sample_environment()
    saved_path = None

    try:
        validate_response = client.post("/api/environments/validate", json=environment)
        assert validate_response.status_code == 200, validate_response.text
        assert validate_response.json()["valid"] is True

        save_response = client.post("/api/environments", json=environment)
        assert save_response.status_code == 200, save_response.text
        saved = save_response.json()
        saved_path = saved["path"]
        assert saved["saved"] is True
        assert os.path.exists(saved_path)

        list_response = client.get("/api/environments")
        assert list_response.status_code == 200
        ids = {item["id"] for item in list_response.json()["environments"]}
        assert "test_web_map" in ids

        get_response = client.get("/api/environments/test_web_map")
        assert get_response.status_code == 200
        assert get_response.json()["bfs_distance"] is not None
    finally:
        if saved_path and os.path.exists(saved_path):
            os.unlink(saved_path)


def test_artifact_download_endpoint_is_scoped_to_run_artifacts():
    client = TestClient(app_module.app)
    artifact_dir = os.path.join("data", "runs", "test_web_api_artifact")
    artifact_path = os.path.join(artifact_dir, "manifest.json")
    os.makedirs(artifact_dir, exist_ok=True)
    with open(artifact_path, "w", encoding="utf-8") as file:
        file.write("{}")

    job = TrainingJob(SimulationConfig(), job_id="test_web_api_artifact")
    job.status = "completed"
    job.progress = 1.0
    job.artifacts = {"manifest_json": artifact_path}
    app_module.jobs.jobs[job.id] = job

    try:
        response = client.get(f"/api/runs/{job.id}/artifacts/manifest_json/download")
        assert response.status_code == 200, response.text
        assert response.content == b"{}"

        missing = client.get(f"/api/runs/{job.id}/artifacts/not_real/download")
        assert missing.status_code == 404
    finally:
        app_module.jobs.jobs.pop(job.id, None)
        shutil.rmtree(artifact_dir, ignore_errors=True)


def test_too_small_procedural_grid_is_rejected():
    client = TestClient(app_module.app)
    response = client.post("/api/train", json={
        "scenario": "B",
        "rows": 5,
        "cols": 5,
        "episodes": 1,
    })
    assert response.status_code == 422

    preview = client.get("/api/environments/preview?scenario=B&rows=5&cols=5&seed=42")
    assert preview.status_code == 400


def test_evaluation_scenarios_are_available_and_valid():
    client = TestClient(app_module.app)
    response = client.get("/api/evaluation-scenarios")
    assert response.status_code == 200, response.text
    scenarios = response.json()["scenarios"]
    assert len(scenarios) >= 4
    for scenario in scenarios:
        environment = scenario["environment"]
        assert environment["rows"] == 20
        assert environment["cols"] == 20
        assert environment["bfs_distance"] is not None
        assert scenario["name"]
        assert scenario["description"]


def test_job_store_loads_persisted_completed_runs():
    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = os.path.join(tmpdir, "runs", "index.json")
        store = JobStore(index_path=index_path)
        job = TrainingJob(SimulationConfig(scenario="B"), job_id="persisted_run")
        job.status = "completed"
        job.progress = 1.0
        job.artifacts = {"qtable_path": "data/runs/persisted_run/qtable.npy"}
        store.jobs[job.id] = job
        with store._lock:
            store._save_index_locked()

        reloaded = JobStore(index_path=index_path)
        snapshot = reloaded.get("persisted_run").snapshot()
        assert snapshot["status"] == "completed"
        assert snapshot["artifacts"]["qtable_path"].endswith("qtable.npy")


if __name__ == "__main__":
    print("=== Teste Web API ===\n")
    test_environment_validate_save_and_list()
    test_artifact_download_endpoint_is_scoped_to_run_artifacts()
    test_too_small_procedural_grid_is_rejected()
    test_evaluation_scenarios_are_available_and_valid()
    test_job_store_loads_persisted_completed_runs()
    print("\n✅ Toate testele Web API au trecut!")
