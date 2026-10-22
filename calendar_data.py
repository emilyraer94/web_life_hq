from datetime import timezone

from database import get_supabase


def _as_utc(value):
    """Convert a timezone-aware date/time to UTC."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Event times must include a timezone.")

    return value.astimezone(timezone.utc)


def load_events(workspace_id, window_start, window_end):
    """Load events overlapping the displayed calendar dates."""
    start = _as_utc(window_start)
    end = _as_utc(window_end)

    if end <= start:
        raise ValueError("The calendar window must end after it starts.")

    records = []
    batch_size = 500

    while True:
        offset = len(records)

        response = (
            get_supabase()
            .table("calendar")
            .select(
                "id, title, starts_at, ends_at, "
                "all_day, location, notes"
            )
            .eq("workspace_id", str(workspace_id))
            .lt("starts_at", end.isoformat())
            .gt("ends_at", start.isoformat())
            .order("starts_at")
            .order("id")
            .range(offset, offset + batch_size - 1)
            .execute()
        )

        batch = response.data
        records.extend(batch)

        if len(batch) < batch_size:
            break

    return records


def _event_values(title, starts_at, ends_at, all_day, location, notes):
    """Validate and prepare an event for the database."""
    start = _as_utc(starts_at)
    end = _as_utc(ends_at)

    if not title.strip() or len(title.strip()) > 160:
        raise ValueError("Enter an event title of 1–160 characters.")

    if end <= start:
        raise ValueError("The event must end after it starts.")

    if len(location) > 240 or len(notes) > 10000:
        raise ValueError("The location or notes exceed the field limits.")

    return {
        "title": title.strip(),
        "starts_at": start.isoformat(),
        "ends_at": end.isoformat(),
        "all_day": bool(all_day),
        "location": location.strip(),
        "notes": notes.strip(),
    }


def add_event(
    workspace_id, title, starts_at, ends_at,
    all_day=False, location="", notes=""
):
    """Add an event to the shared calendar."""
    values = _event_values(
        title, starts_at, ends_at, all_day, location, notes
    )

    response = (
        get_supabase()
        .table("calendar")
        .insert({
            "workspace_id": str(workspace_id),
            **values,
        })
        .execute()
    )

    return response.data


def save_event(
    workspace_id, event_id, title, starts_at, ends_at,
    all_day=False, location="", notes=""
):
    """Save changes to an existing shared event."""
    values = _event_values(
        title, starts_at, ends_at, all_day, location, notes
    )

    response = (
        get_supabase()
        .table("calendar")
        .update(values)
        .eq("id", str(event_id))
        .eq("workspace_id", str(workspace_id))
        .execute()
    )

    if not response.data:
        raise ValueError(
            "This event could not be updated. "
            "Refresh to check its current state."
        )

    return response.data