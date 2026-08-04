from app.services.calendar_store import events, get_events, save_event


def test_save_event_and_get_events():
    events.clear()
    result = save_event("Doctor appointment", "2026-06-01", "15:00", "Annual checkup")

    assert result["status"] == "success"
    assert result["event"]["title"] == "Doctor appointment"
    assert get_events()["events"][0]["time"] == "15:00"


def test_save_event_rejects_invalid_time():
    events.clear()
    result = save_event("Meeting", "2026-06-01", "7:30 PM")

    assert result["status"] == "error"
