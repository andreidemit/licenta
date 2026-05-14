"""Client OpenAI-compatible pentru Ollama/Gemma."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterator

import httpx


class LlmClientError(RuntimeError):
    """Eroare controlată pentru indisponibilitatea sau răspunsul invalid al LLM-ului."""


@dataclass(frozen=True)
class LlmClient:
    base_url: str
    model: str
    provider: str = "ollama"
    timeout_seconds: float = 60.0
    max_output_tokens: int = 700

    @property
    def chat_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/chat/completions"

    @property
    def native_ollama_chat_url(self) -> str:
        base_url = self.base_url.rstrip("/")
        if base_url.endswith("/v1"):
            base_url = base_url[:-3]
        return f"{base_url}/api/chat"

    @property
    def models_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/models"

    def health(self) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=min(self.timeout_seconds, 10.0)) as client:
                response = client.get(self.models_url)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            raise LlmClientError(str(exc)) from exc
        models = payload.get("data") if isinstance(payload, dict) else None
        model_ids = [
            item.get("id")
            for item in (models or [])
            if isinstance(item, dict) and item.get("id")
        ]
        model_available = self.model in model_ids
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "available": model_available,
            "models": model_ids,
            "message": (
                "Modelul configurat este disponibil."
                if model_available
                else f"Ollama răspunde, dar modelul configurat nu este în listă: {self.model}"
            ),
        }

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self.max_output_tokens,
            "stream": False,
            "response_format": {"type": "json_object"},
        }
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(self.chat_url, json=payload)
                try:
                    response.raise_for_status()
                    data = response.json()
                    content = self._extract_openai_content(data)
                    if content:
                        return content
                except httpx.HTTPStatusError:
                    if self.provider != "ollama":
                        raise
                if self.provider == "ollama":
                    return self._chat_native_ollama(client, messages, temperature)
        except LlmClientError:
            raise
        except Exception as exc:
            raise LlmClientError(str(exc)) from exc

        raise LlmClientError("Răspuns LLM invalid: conținut gol")

    def _chat_native_ollama(
        self,
        client: httpx.Client,
        messages: list[dict[str, str]],
        temperature: float,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": False,
            "format": "json",
            "options": {
                "temperature": temperature,
                "num_predict": self.max_output_tokens,
            },
        }
        response = client.post(self.native_ollama_chat_url, json=payload)
        response.raise_for_status()
        data = response.json()
        content = self._extract_native_ollama_content(data)
        if not content:
            raise LlmClientError("Răspuns LLM invalid: conținut gol")
        return content

    def chat_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> Iterator[str]:
        """Iterează tokenii returnați de LLM. Nu folosește JSON mode."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self.max_output_tokens,
            "stream": True,
        }
        try:
            client = httpx.Client(timeout=self.timeout_seconds)
        except Exception as exc:
            raise LlmClientError(str(exc)) from exc

        try:
            try:
                with client.stream("POST", self.chat_url, json=payload) as response:
                    if response.status_code >= 400:
                        if self.provider == "ollama":
                            yield from self._stream_native_ollama(client, messages, temperature)
                            return
                        response.raise_for_status()
                    yielded = False
                    for token in self._iter_openai_sse(response):
                        yielded = True
                        yield token
                    if yielded:
                        return
                    if self.provider == "ollama":
                        yield from self._stream_native_ollama(client, messages, temperature)
                        return
            except httpx.HTTPStatusError:
                if self.provider != "ollama":
                    raise
                yield from self._stream_native_ollama(client, messages, temperature)
        except LlmClientError:
            raise
        except Exception as exc:
            raise LlmClientError(str(exc)) from exc
        finally:
            client.close()

    @staticmethod
    def _iter_openai_sse(response: httpx.Response) -> Iterator[str]:
        for raw_line in response.iter_lines():
            line = raw_line.strip() if isinstance(raw_line, str) else ""
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if not data or data == "[DONE]":
                if data == "[DONE]":
                    return
                continue
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                continue
            choices = payload.get("choices") if isinstance(payload, dict) else None
            if not choices:
                continue
            delta = choices[0].get("delta") if isinstance(choices[0], dict) else None
            content = delta.get("content") if isinstance(delta, dict) else None
            if isinstance(content, str) and content:
                yield content

    def _stream_native_ollama(
        self,
        client: httpx.Client,
        messages: list[dict[str, str]],
        temperature: float,
    ) -> Iterator[str]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "think": False,
            "options": {
                "temperature": temperature,
                "num_predict": self.max_output_tokens,
            },
        }
        with client.stream("POST", self.native_ollama_chat_url, json=payload) as response:
            response.raise_for_status()
            for raw_line in response.iter_lines():
                line = raw_line.strip() if isinstance(raw_line, str) else ""
                if not line:
                    continue
                try:
                    payload_obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(payload_obj, dict):
                    continue
                if payload_obj.get("done"):
                    return
                message = payload_obj.get("message")
                if isinstance(message, dict):
                    content = message.get("content")
                    if isinstance(content, str) and content:
                        yield content
                else:
                    chunk = payload_obj.get("response")
                    if isinstance(chunk, str) and chunk:
                        yield chunk

    @staticmethod
    def _extract_openai_content(data: dict[str, Any]) -> str:
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return ""
        return content.strip() if isinstance(content, str) else ""

    @staticmethod
    def _extract_native_ollama_content(data: dict[str, Any]) -> str:
        message = data.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
        response = data.get("response")
        return response.strip() if isinstance(response, str) else ""
