import asyncio

from SandboxAdapter.Converter import SandboxConverter
from SandboxAdapter.Core import SandboxAdapter


def _convert(raw):
    return SandboxConverter("bot_1").convert(raw)


def test_request_flag_mapped_to_request_id():
    event = _convert(
        {"type": "request", "request_type": "friend", "user_id": "u1", "flag": "flag_1", "comment": "加个好友"}
    )
    assert event["type"] == "request"
    assert event["detail_type"] == "friend"
    assert event["user_id"] == "u1"
    assert event["request_id"] == "flag_1"


def test_request_native_id_preferred():
    event = _convert(
        {"type": "request", "request_type": "friend", "user_id": "u1", "request_id": "rid_9", "flag": "flag_1"}
    )
    assert event["request_id"] == "rid_9"


def test_request_id_falls_back_to_raw_id():
    event = _convert({"type": "request", "request_type": "group", "user_id": "u1", "id": "raw_7", "group_id": "g1"})
    assert event["detail_type"] == "group"
    assert event["request_id"] == "raw_7"
    assert event["group_id"] == "g1"


def test_request_without_id_not_synthesized():
    event = _convert({"type": "request", "request_type": "friend", "user_id": "u1"})
    assert event["type"] == "request"
    assert "request_id" not in event


class _StubAdapter:
    _platform = "sandbox"

    def make_response(self, *, status="ok", retcode=0, data=None, message_id="", message="", raw=None):
        return {"status": status, "retcode": retcode, "data": data, "message_id": message_id, "message": message}


def test_request_stub_accept_reject_format():
    async def _do():
        adapter = _StubAdapter()
        accepted = await SandboxAdapter.Request(adapter, "flag_1").accept()
        assert accepted == {"status": "ok", "retcode": 0, "data": None, "message_id": "", "message": ""}
        rejected = await SandboxAdapter.Request(adapter, "flag_1").reject()
        assert rejected == {"status": "ok", "retcode": 0, "data": None, "message_id": "", "message": ""}

    asyncio.run(_do())
