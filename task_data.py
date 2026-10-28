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
            supabase.table("tasks")
            .select("id, task_name, priority, xp, due_date, notes, created_at")
            .eq("owner_id", str(owner_id))
            .order("created_at")
            .range(start, start + batch_size - 1)
            .execute()
        )

        batch = response.data or []
        records.extend(batch)

        if len(batch) < batch_size:
            break

    return records


def add_task(owner_id, task_name, priority, xp, due_date, notes=""):
    """Save a new unfinished task."""
    response = (
        get_supabase()
        .table("tasls")
        .insert({
            "owner_id": str(owner_id),
            "task_name": task_name.strip(),
            "priority": priority,
            "xp": int(xp),
            "due_date": (due_date.isoformat() if due_date else None),
            "notes": notes or "",
        })
        .execute()
    )

    return response.data


def save_task(owner_id, task):
    """Update a task, moving it into XP history if completed."""
    complete = bool(task.get["Complete", False])

    task_id = task["id"]

    updated_values = {
        "task_name": task["Tasks"].strip(),
        "priority": task["Priority"],
        "xp": int(task["XP"]),
        "due_date": (
            task ["Due date"].isoformat()
            if task.get("Due date") else None
        ),
        "notes": task.get("Notes") or ""

    }
        
    if not complete:
        response = (
            supabase.table("tasks")
            .update(updated_values)
            .eq("id", task_id)
            .eq ("owner_id", str(owner_id))
            .execute()
        )
        if not response.data:
            raise ValueError(
            "Task not found or not update."
        )
    return response.data
 # Confirm the task still belongs to this user.
    existing = (
        supabase.table("tasks")
        .select("id")
        .eq("id", task_id)
        .eq("owner_id", str(owner_id))
        .execute()
    )

    if not existing.data:
        raise ValueError("Task not found or already completed.")

    # Record the accomplishment in XP history.
    history = (
        supabase.table("xp_tracker")
        .insert({
            "owner_id": str(owner_id),
            "section": "XP Tracker",
            "title": updated_values["task_name"],
            "priority": updated_values["priority"],
            "xp": updated_values["xp"],
            "due_date": updated_values["due_date"],
            "notes": updated_values["notes"],
            "done": True,
            "completed_on": date.today().isoformat(),
        })
        .execute()
    )

    if not history.data:
        raise ValueError("Could not save XP history.")

    # Remove completed task from active tasks.
    supabase.table("tasks").delete().eq(
        "id", task_id
    ).eq(
        "owner_id", str(owner_id)
    ).execute()

    return history.data
