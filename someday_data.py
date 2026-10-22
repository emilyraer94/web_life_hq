from database import get_supabase


def load_someday_items(workspace_id):
    """Load items belonging to the shared workspace."""
    records = []
    batch_size = 500

    while True:
        start = len(records)

        response = (
            get_supabase()
            .table("someday_items")
            .select("id, title,category, notes")
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


def add_someday_item(workspace_id, name, notes, category="Other"):
    """Save a new item to the shared workspace."""
    response = (
        get_supabase()
        .table("someday_items")
        .insert({
            "workspace_id": str(workspace_id),
            "title": name.strip(),
            "notes": notes.strip(),
            "category": category,
        })
        .execute()
    )

    return response.data


def save_someday_item(workspace_id, item):
    """Save edits to an existing shared item."""
    response = (
        get_supabase()
        .table("someday_items")
        .update({
            "title": item["Item"].strip(),
            "notes": (item["Notes"] or "").strip(),
            "category": item.get("Category", "Other"),
        })
        .eq("id", item["id"])
        .eq("workspace_id", str(workspace_id))
        .execute()
    )

    if not response.data:
        raise ValueError(
            "This item could not be updated. "
            "Refresh to check its current state."
        )

    return response.data