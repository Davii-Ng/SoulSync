from datetime import datetime, timezone


def make_ws_message(msg_type: str, payload: dict) -> dict:
    """Build a WebSocket envelope matching the contract in CLAUDE.md."""
    return {
        "type": msg_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
