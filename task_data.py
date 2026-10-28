
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
            .select(
                "id, task_name, priority, xp, "
                "due_date, notes, created_at"
            )
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


def add_task(
    owner_id,
    task_name,
    priority,
    xp,
    due_date,
    notes=""
):
    """Save a new unfinished task."""
    task_name = task_name.strip()

    if not task_name:
        raise ValueError("Task name cannot be empty.")

    response = (
        get_supabase()
        .table("tasks")
        .insert({
            "owner_id": str(owner_id),
            "task_name": task_name,
            "priority": priority,
            "xp": int(xp),
            "due_date": (
                due_date.isoformat()
                if due_date else None
            ),
            "notes": notes or "",
        })
        .execute()
    )

    return response.data


def save_task(owner_id, task):
    """Update a task or complete it for XP."""
    supabase = get_supabase()

    complete = bool(task.get("Complete", False))
    task_id = task["id"]

    task_name = task["Task"].strip()

    if not task_name:
        raise ValueError("Task name cannot be empty.")

    due_date = task.get("Due date")

    updated_values = {
        "task_name": task_name,
        "priority": task["Priority"],
        "xp": int(task["XP"]),
        "due_date": (
            due_date.isoformat()
            if due_date else None
        ),
        "notes": task.get("Notes") or "",
    }

    # Save changes to an unfinished task.
    if not complete:
        response = (
            supabase.table("tasks")
            .update(updated_values)
            .eq("id", task_id)
            .eq("owner_id", str(owner_id))
            .execute()
        )

        if not response.data:
            raise ValueError(
                "Task not found or not updated."
            )

        return response.data

    # Complete the task using one database transaction.
    # The database function verifies task ownership,
    # moves the task into XP history, and removes it
    # from active tasks.
    response = (
        supabase.rpc(
            "complete_task",
            {
                "p_task_id": task_id,
                "p_task_name": task_name,
                "p_priority": updated_values["priority"],
                "p_xp": updated_values["xp"],
                "p_due_date": updated_values["due_date"],
                "p_notes": updated_values["notes"],
            },
        )
        .execute()
    )

    return response.data
