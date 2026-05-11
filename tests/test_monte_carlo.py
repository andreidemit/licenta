"""Smoke tests pentru pipeline-ul Monte Carlo (experiments + endpoint)."""

from fastapi.testclient import TestClient

from experiments.compare_agents import (
    EXPERIMENT_PROFILES,
    run_monte_carlo_experiment,
)
from web.backend.app import app


def test_known_static_returns_complete_summary():
    result = run_monte_carlo_experiment(
        agents=["random", "astar"],
        experiment_profile="known_static",
        scenario="medium",
        number_of_maps=3,
        episodes_per_map=2,
        training_episodes=0,
        max_steps=80,
        random_seed=11,
    )

    assert result["summary"]["episode_count"] == 12
    algorithms = {row["algorithm"] for row in result["summary"]["agents"]}
    assert algorithms == {"Random", "A*"}

    for row in result["summary"]["agents"]:
        assert "reward_distribution" in row
        for key in ("mean", "std", "p25", "p50", "p75", "ci95_low", "ci95_high"):
            assert key in row["reward_distribution"]
        assert row["success_rate_ci95_low"] <= row["success_rate"] <= row["success_rate_ci95_high"]

    per_map = result["summary"]["per_map"]
    assert per_map, "per_map ar trebui populat când map_seed este atașat"
    seeds = {entry["map_seed"] for entry in per_map}
    assert len(seeds) == 3


def test_per_map_omitted_when_seed_missing():
    """Smoke: aggregate_results trebuie să tolereze episoade fără map_seed."""
    from simulation.episode_result import EpisodeResult
    from simulation.metrics import aggregate_results

    episodes = [
        EpisodeResult(
            algorithm="x",
            success=True,
            total_reward=1.0,
            steps=2,
            collisions=0,
            danger_entries=0,
            total_risk_exposure=0.0,
            path=[(0, 0), (0, 1)],
            reached_goal=True,
            timeout=False,
            events=[],
        )
    ]
    summary = aggregate_results(episodes)
    assert summary["per_map"] == []
    assert summary["episode_count"] == 1


def test_transfer_learning_uses_distinct_train_eval_seeds():
    result = run_monte_carlo_experiment(
        agents=["astar"],
        experiment_profile="transfer_learning",
        scenario="medium",
        number_of_maps=2,
        episodes_per_map=1,
        training_episodes=2,
        max_steps=60,
        random_seed=7,
    )
    eval_seeds = {episode["map_seed"] for episode in result["episodes"]}
    train_offset = 7 + 50_000
    assert all(seed not in {train_offset, train_offset + 997} for seed in eval_seeds), (
        "Seed-urile de evaluare nu trebuie să se suprapună cu cele de training."
    )
    assert result["profile"]["id"] == "transfer_learning"


def test_all_profiles_declare_agent_lifecycle():
    for profile in EXPERIMENT_PROFILES.values():
        assert "agent_lifecycle" in profile, f"Profil {profile['id']} nu declară agent_lifecycle"
        assert profile["agent_lifecycle"] in {"per_map", "shared_across_maps"}


def test_monte_carlo_endpoint_returns_extended_summary():
    client = TestClient(app)
    response = client.post(
        "/api/safe-navigation/monte-carlo",
        json={
            "algorithms": ["random", "astar"],
            "experiment_profile": "known_static",
            "scenario": "medium",
            "number_of_maps": 2,
            "episodes_per_map": 1,
            "training_episodes": 0,
            "max_steps": 60,
            "random_seed": 5,
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["summary"]["episode_count"] == 4
    assert payload["summary"]["per_map"], "endpoint-ul trebuie să expună per_map"
    sample = payload["summary"]["agents"][0]
    assert "reward_distribution" in sample
    assert "success_rate_ci95_low" in sample
    assert payload["episodes"][0]["map_seed"] is not None


if __name__ == "__main__":
    test_known_static_returns_complete_summary()
    test_per_map_omitted_when_seed_missing()
    test_transfer_learning_uses_distinct_train_eval_seeds()
    test_all_profiles_declare_agent_lifecycle()
    test_monte_carlo_endpoint_returns_extended_summary()
    print("OK")
