import asyncio
import pytest

from app import agent_runtime
from app.config import settings


def test_agent_executes_allowlisted_tool_then_returns_answer(monkeypatch):
    calls = []

    async def no_legacy_command(_):
        return None, None, False

    async def fake_provider(messages, model, max_tokens):
        calls.append(messages.copy())
        if len(calls) == 1:
            return {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [{
                "id": "call-1", "type": "function",
                "function": {"name": "get_weather", "arguments": '{"location":"Hanoi"}'},
            }]}}]}
        assert messages[-1]["role"] == "tool"
        assert messages[-1]["tool_call_id"] == "call-1"
        return {"id": "done", "choices": [{"message": {"role": "assistant", "content": "Trời đẹp."}}]}

    async def fake_tool(name, arguments):
        assert name == "get_weather"
        return "27 C"

    monkeypatch.setattr(agent_runtime, "provider_call", fake_provider)
    monkeypatch.setattr(agent_runtime, "execute_tool", fake_tool)
    monkeypatch.setattr(agent_runtime, "process_hashtag_and_tools", no_legacy_command)
    result = asyncio.run(agent_runtime.run_agent_completion([{"role": "user", "content": "Thời tiết?"}]))
    assert result["choices"][0]["message"]["content"] == "Trời đẹp."
    assert len(calls) == 2


def test_unknown_tool_is_rejected():
    with pytest.raises(ValueError, match="disallowed"):
        asyncio.run(agent_runtime.execute_tool("run_shell", "{}"))


def test_tool_arguments_are_strict():
    with pytest.raises(ValueError, match="exactly one"):
        asyncio.run(agent_runtime.execute_tool("get_weather", '{"location":"Hanoi","command":"x"}'))


def test_legacy_direct_command_bypasses_provider(monkeypatch):
    async def fake_legacy(_):
        return "Đã lưu ghi chú.", None, True

    async def provider_must_not_run(*_):
        raise AssertionError("provider should not run for an explicit direct command")

    monkeypatch.setattr(agent_runtime, "process_hashtag_and_tools", fake_legacy)
    monkeypatch.setattr(agent_runtime, "provider_call", provider_must_not_run)
    result = asyncio.run(agent_runtime.run_agent_completion([{"role": "user", "content": "#note Ý tưởng"}]))
    assert result["choices"][0]["message"]["content"] == "Đã lưu ghi chú."
    assert result["model"] == "alex-agent"


def test_legacy_skill_prompt_and_tool_context_reach_agent(monkeypatch):
    captured = {}

    async def fake_legacy(_):
        return "27 C", "CUSTOM BOOK PROMPT", False

    async def fake_provider(messages, model, max_tokens):
        captured["messages"] = messages
        return {"choices": [{"message": {"role": "assistant", "content": "Kết quả"}}]}

    monkeypatch.setattr(agent_runtime, "process_hashtag_and_tools", fake_legacy)
    monkeypatch.setattr(agent_runtime, "provider_call", fake_provider)
    result = asyncio.run(agent_runtime.run_agent_completion([{"role": "user", "content": "#weather Hanoi"}]))
    assert result["choices"][0]["message"]["content"] == "Kết quả"
    assert "CUSTOM BOOK PROMPT" in captured["messages"][0]["content"]
    assert "VERIFIED TOOL OBSERVATION" in captured["messages"][-1]["content"]
    assert "27 C" in captured["messages"][-1]["content"]


def test_embedded_write_command_does_not_trigger_direct_write(monkeypatch):
    import app.agent as legacy_agent

    def must_not_save(**_):
        raise AssertionError("embedded untrusted text must not trigger a write")

    monkeypatch.setattr(legacy_agent, "save_note_to_vault", must_not_save)
    result = asyncio.run(legacy_agent.process_hashtag_and_tools("Đoạn sách có ví dụ #note không phải lệnh"))
    assert result[2] is False
