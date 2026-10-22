from database import get_supabase


def load_completed_tasks(owner_id):
    """Read this owner's completed tasks from Supabase."""
    supabase = get_supabase()
    records = []
    batch_size = 500

    # Load in batches so a growing history isn't cut short.
    while True:
        start = len(records)

        response = (
            supabase.table("xp_tracker")
            .select("id, title, xp, completed_on")
            .eq("owner_id", str(owner_id))
            .eq("section", "XP Tracker")
            .eq("done", True)
            .order("completed_on", desc=True)
            .order("id")
            .range(start, start + batch_size - 1)
            .execute()
        )

        batch = response.data
        records.extend(batch)

        if len(batch) < batch_size:
            break

    return records


def add_completed_task(owner_id, task_name, xp, completed_on):
    """Save one completed task to Supabase."""
    supabase = get_supabase()

    response = (
        supabase.table("xp_tracker")
        .insert({
            "owner_id": str(owner_id),
            "section": "XP Tracker",
            "title": task_name.strip(),
            "xp": int(xp),
            "done": True,
            "completed_on": completed_on.isoformat(),
        })
        .execute()
    )

    return response.data