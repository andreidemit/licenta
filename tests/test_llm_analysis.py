"""Teste pentru stratul Analist AI bazat pe Ollama/OpenAI-compatible API."""

from web.backend.llm_analysis import (
    build_messages,
    disabled_response,
    parse_analysis_response,
)
from web.backend.llm_client import LlmClient
from web.backend.models import LlmAnalysisRequest


def _request() -> LlmAnalysisRequest:
    return LlmAnalysisRequest(
        config={"scenario": "medium", "number_of_maps": 3},
        summary={
            "agents": [
                {
                    "algorithm": "Risk-Aware A*",
                    "success_rate": 1.0,
                    "average_risk_exposure": 4.0,
                    "average_total_cost": 42.0,
                }
            ]
        },
        recommendation={
            "objective": "safety_first",
            "recommended_algorithm": "Risk-Aware A*",
            "ranking": [{"algorithm": "Risk-Aware A*", "score": 0.91}],
            "tradeoffs": ["Traseu ușor mai lung, risc mai mic."],
        },
        question="Explică recomandarea.",
    )


def test_build_messages_includes_summary_recommendation_and_truncates():
    request = _request()
    request.summary["raw_episode_excerpt"] = ["x" * 2000]
    messages = build_messages(request, max_input_chars=1000)

    assert messages[0]["role"] == "system"
    assert "Recomandarea este calculată determinist" in messages[0]["content"]
    user_content = messages[1]["content"]
    assert "summary" in user_content
    assert "recommendation" in user_content
    assert "truncated" in user_content


def test_parse_analysis_response_accepts_json_and_raw_fallback():
    response = parse_analysis_response(
        '{"answer":"OK","key_points":["punct"],"limitations":["limitare"],"used_metrics":["success_rate"]}',
        model="gemma4:26b",
        provider="ollama",
    )
    assert response.answer == "OK"
    assert response.key_points == ["punct"]
    assert response.used_metrics == ["success_rate"]
    assert response.fallback is False

    fallback = parse_analysis_response("text brut", model="gemma4:26b", provider="ollama")
    assert fallback.answer == "text brut"
    assert fallback.fallback is True
    assert fallback.limitations


def test_disabled_response_is_clear_fallback():
    response = disabled_response(model="gemma4:26b", provider="ollama")

    assert response.fallback is True
    assert "dezactivat" in response.answer.lower()
    assert response.model == "gemma4:26b"


def test_llm_client_builds_openai_compatible_chat_request():
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": '{"answer":"OK"}'}}]}

    class FakeHttpClient:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, json):
            captured["url"] = url
            captured["payload"] = json
            return FakeResponse()

    import web.backend.llm_client as llm_client_module

    original_client = llm_client_module.httpx.Client
    llm_client_module.httpx.Client = FakeHttpClient
    try:
        client = LlmClient(
            base_url="http://127.0.0.1:11434/v1/",
            model="gemma4:26b",
            timeout_seconds=12,
        )
        content = client.chat([{"role": "user", "content": "test"}])
    finally:
        llm_client_module.httpx.Client = original_client

    assert content == '{"answer":"OK"}'
    assert captured["url"] == "http://127.0.0.1:11434/v1/chat/completions"
    assert captured["timeout"] == 12
    assert captured["payload"]["model"] == "gemma4:26b"
    assert captured["payload"]["max_tokens"] == 700
    assert captured["payload"]["response_format"] == {"type": "json_object"}
    assert captured["payload"]["stream"] is False


def test_llm_client_falls_back_to_native_ollama_when_content_is_empty():
    captured = {"urls": [], "payloads": []}

    class FakeOpenAiResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "", "reasoning": "json în reasoning"}}]}

    class FakeNativeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": '{"answer":"OK native"}'}}

    class FakeHttpClient:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, json):
            captured["urls"].append(url)
            captured["payloads"].append(json)
            if url.endswith("/v1/chat/completions"):
                return FakeOpenAiResponse()
            return FakeNativeResponse()

    import web.backend.llm_client as llm_client_module

    original_client = llm_client_module.httpx.Client
    llm_client_module.httpx.Client = FakeHttpClient
    try:
        client = LlmClient(
            base_url="http://127.0.0.1:11434/v1",
            model="gemma4:26b",
            provider="ollama",
        )
        content = client.chat([{"role": "user", "content": "test"}])
    finally:
        llm_client_module.httpx.Client = original_client

    assert content == '{"answer":"OK native"}'
    assert captured["urls"] == [
        "http://127.0.0.1:11434/v1/chat/completions",
        "http://127.0.0.1:11434/api/chat",
    ]
    assert captured["payloads"][1]["think"] is False
    assert captured["payloads"][1]["format"] == "json"
    assert captured["payloads"][1]["options"]["num_predict"] == 700


if __name__ == "__main__":
    test_build_messages_includes_summary_recommendation_and_truncates()
    test_parse_analysis_response_accepts_json_and_raw_fallback()
    test_disabled_response_is_clear_fallback()
    test_llm_client_builds_openai_compatible_chat_request()
    test_llm_client_falls_back_to_native_ollama_when_content_is_empty()
    print("OK")
