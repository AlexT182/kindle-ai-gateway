import asyncio
import pytest

from app import agent_runtime
from app.config import settings


def test_agent_executes_allowlisted_tool_then_returns_answer(monkeypatch):
    calls = []

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
    result = asyncio.run(agent_runtime.run_agent_completion([{"role": "user", "content": "Thời tiết?"}]))
    assert result["choices"][0]["message"]["content"] == "Trời đẹp."
    assert len(calls) == 2


def test_unknown_tool_is_rejected():
    with pytest.raises(ValueError, match="disallowed"):
        asyncio.run(agent_runtime.execute_tool("run_shell", "{}"))


def test_tool_arguments_are_strict():
    with pytest.raises(ValueError, match="exactly one"):
        asyncio.run(agent_runtime.execute_tool("get_weather", '{"location":"Hanoi","command":"x"}'))
