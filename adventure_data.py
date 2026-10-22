from database import get_supabase


def get_shared_workspace_id(user_id):
    """Find the shared workspace this user belongs to."""
    response = (
        get_supabase()
        .table("workspace_members")
        .select("workspace_id")
        .eq("user_id", str(user_id))
        .execute()
    )

    if len(response.data) != 1:
        raise ValueError("Expected one shared workspace for this account.")

    return response.data[0]["workspace_id"]


def load_adventures(workspace_id):
    """Load the destinations in this shared workspace."""
    records = []
    batch_size = 500

    while True:
        start = len(records)

        response = (
            get_supabase()
            .table("adventures")
            .select("id, title, location, status, notes")
            .eq("workspace_id", str(workspace_id))
            .order("created_at")
            .order("id")
            .range(start, start + batch_size - 1)
            .execute()
        )

        batch = response.data
        records.extend(batch)

        if len(batch) < batch_size:
            break

    return records


def add_adventure(user_id, workspace_id, name, location, status, notes):
    """Save a new destination to the shared workspace."""
    response = (
        get_supabase()
        .table("adventures")
        .insert({
            "workspace_id": str(workspace_id),
            "created_by": str(user_id),
            "title": name.strip(),
            "location": location.strip(),
            "status": status,
            "notes": notes.strip(),
        })
        .execute()
    )

    return response.data


def save_adventure(workspace_id, adventure):
    """Save edits to an existing shared destination."""
    response = (
        get_supabase()
        .table("adventures")
        .update({
            "title": adventure["Adventure"].strip(),
            "location": (adventure["Location"] or "").strip(),
            "status": adventure["Status"],
            "notes": (adventure["Notes"] or "").strip(),
        })
        .eq("id", adventure["id"])
        .eq("workspace_id", str(workspace_id))
        .execute()
    )

    if not response.data:
        raise ValueError(
            "This adventure could not be updated. "
            "Refresh to check its current state."
        )

    return response.data