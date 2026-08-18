from __future__ import annotations

from app.core.logging import redact_value


def test_redact_secret_keys() -> None:
    assert redact_value("hf_token", "abc") == "***"
    assert redact_value("OIDC_CLIENT_SECRET", "abc") == "***"
    assert redact_value("authorization", "Bearer xyz") == "***"
    assert redact_value("api_key", "sk-live") == "***"
    assert redact_value("model_id", "qwen3") == "qwen3"
