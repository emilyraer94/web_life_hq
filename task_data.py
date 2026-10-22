from datetime import date

from database import get_supabase


def load_tasks(owner_id):
    """Load this owner's unfinished tasks."""
    supabase = get_supabase()
    records = []
    batch_size = 500

    while True:
        start = len(records)

        response = (
            supabase.table("xp_tracker")
            .select("id, title, priority, xp, due_date")
            .eq("owner_id", str(owner_id))
            .eq("section", "Tasks")
            .eq("done", False)
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


def add_task(owner_id, task_name, priority, xp, due_date):
    """Save a new unfinished task."""
    response = (
        get_supabase()
        .table("xp_tracker")
        .insert({
            "owner_id": str(owner_id),
            "section": "Tasks",
            "title": task_name.strip(),
            "priority": priority,
            "xp": int(xp),
            "due_date": due_date.isoformat() if due_date else None,
            "done": False,
        })
        .execute()
    )

    return response.data


def save_task(owner_id, task):
    """Update a task, moving it into XP history if completed."""
    complete = bool(task["Complete"])

    response = (
        get_supabase()
        .table("xp_tracker")
        .update({
            "title": task["Task"].strip(),
            "priority": task["Priority"],
            "xp": int(task["XP"]),
            "due_date": (
                task["Due date"].isoformat()
                if task["Due date"]
                else None
            ),
            "done": complete,
            "section": "XP Tracker" if complete else "Tasks",
            "completed_on": date.today().isoformat() if complete else None,
        })
        .eq("id", task["id"])
        .eq("owner_id", str(owner_id))
        .eq("section", "Tasks")
        .eq("done", False)
        .execute()
    )

    if not response.data:
        raise ValueError(
            "This task could not be updated. Refresh the page "
            "to load its current state."
        )

    return response.data