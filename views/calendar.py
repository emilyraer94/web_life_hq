import calendar
from datetime import datetime, time, timedelta, timezone
from html import escape
from zoneinfo import ZoneInfo

import streamlit as st
from httpx import HTTPError
from postgrest.exceptions import APIError

from auth import require_login
from adventure_data import get_shared_workspace_id
from calendar_data import add_event, load_events, save_event


TZ = ZoneInfo("America/Indiana/Indianapolis")


def local_datetime(day, clock):
    """Apply Indiana time and reject nonexistent daylight-saving times."""
    naive = datetime.combine(day, clock)
    aware = naive.replace(tzinfo=TZ)

    round_trip = (
        aware.astimezone(timezone.utc)
        .astimezone(TZ)
        .replace(tzinfo=None)
    )

    if round_trip != naive:
        raise ValueError(
            "That time does not exist because of daylight saving time. "
            "Please choose another time."
        )

    return aware


st.title("🗓️ Shared Calendar", anchor=False)
st.caption("Shared with Will • All times shown in Indiana time.")

user = require_login()

selected_date = st.date_input(
    "Choose a date in the month to view",
    value=datetime.now(TZ).date(),
    key="calendar_month",
)

month_start = selected_date.replace(day=1)
next_month = (
    month_start.replace(day=28) + timedelta(days=4)
).replace(day=1)

window_start = local_datetime(month_start, time.min)
window_end = local_datetime(next_month, time.min)

try:
    workspace_id = get_shared_workspace_id(user.id)
    records = load_events(workspace_id, window_start, window_end)
except ValueError as error:
    st.error(str(error))
    st.stop()
except (APIError, HTTPError):
    st.error("Could not load the calendar. Please refresh to try again.")
    st.stop()

# Convert saved timestamps into Indiana time.
events = [
    {
        **record,
        "start": datetime.fromisoformat(
            record["starts_at"].replace("Z", "+00:00")
        ).astimezone(TZ),
        "end": datetime.fromisoformat(
            record["ends_at"].replace("Z", "+00:00")
        ).astimezone(TZ),
    }
    for record in records
]

st.metric("Events this month", len(events))

# Build the event labels for each calendar day.
events_by_day = {}
day = month_start

while day < next_month:
    day_start = local_datetime(day, time.min).astimezone(timezone.utc)
    day_end = local_datetime(
        day + timedelta(days=1), time.min
    ).astimezone(timezone.utc)

    labels = []

    for event in events:
        event_start = event["start"].astimezone(timezone.utc)
        event_end = event["end"].astimezone(timezone.utc)

        if event_start < day_end and event_end > day_start:
            if event["all_day"]:
                prefix = "All day"
            elif event["start"].date() == day:
                prefix = event["start"].strftime("%I:%M %p").lstrip("0")
            else:
                prefix = "Continues"

            labels.append(f"{prefix} · {event['title']}")

    events_by_day[day.day] = labels
    day += timedelta(days=1)


class SharedMonth(calendar.HTMLCalendar):
    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="empty"></td>'

        labels = events_by_day.get(day, [])
        event_html = "".join(
            f'<div class="event">{escape(label)}</div>'
            for label in labels[:3]
        )

        if len(labels) > 3:
            event_html += (
                f'<div class="more">+{len(labels) - 3} more</div>'
            )

        return (
            f'<td><strong>{day}</strong>'
            f"{event_html}</td>"
        )


month_html = SharedMonth(firstweekday=6).formatmonth(
    selected_date.year,
    selected_date.month,
)

st.html(
    """
    <style>
    .lhq-calendar {
        overflow-x: auto;
        margin-bottom: 1rem;
    }
    .lhq-calendar table {
        width: 100%;
        min-width: 560px;
        table-layout: fixed;
        border-collapse: collapse;
        font: inherit;
        color: inherit;
    }
    .lhq-calendar th {
        padding: 8px;
        text-align: center;
    }
    .lhq-calendar td {
        border: 1px solid #8886;
        height: 105px;
        padding: 6px;
        vertical-align: top;
    }
    .lhq-calendar .empty {
        opacity: 0.3;
    }
    .lhq-calendar .event {
        margin-top: 5px;
        padding: 4px;
        border-radius: 4px;
        background: #6688aa26;
        font-size: 0.75rem;
        overflow-wrap: anywhere;
    }
    .lhq-calendar .more {
        margin-top: 5px;
        font-size: 0.75rem;
    }
    </style>
    """
    + f'<div class="lhq-calendar">{month_html}</div>'
)

st.subheader("Events this month", anchor=False)

if events:
    rows = []

    for event in events:
        if event["all_day"]:
            start_label = event["start"].strftime("%b %d, %Y")
            end_label = (
                event["end"] - timedelta(microseconds=1)
            ).strftime("%b %d, %Y")
        else:
            start_label = event["start"].strftime("%b %d, %Y %I:%M %p")
            end_label = event["end"].strftime("%b %d, %Y %I:%M %p")

        rows.append({
            "Event": event["title"],
            "Start": start_label,
            "End": end_label,
            "All day": event["all_day"],
            "Location": event["location"],
            "Notes": event["notes"],
        })

    st.dataframe(rows, hide_index=True, width="stretch")
else:
    st.info("No events in this month yet.")

st.subheader("Add an event", anchor=False)

# Outside the form so switching it immediately updates the time inputs.
all_day = st.toggle("All-day event", key="new_event_all_day")

with st.form("add_calendar_event", clear_on_submit=True):
    title = st.text_input("Event title", max_chars=160)

    start_date = st.date_input("Start date", value=selected_date)
    end_date = st.date_input(
        "End date",
        value=selected_date,
        help="For all-day events, choose the last day included.",
    )

    if not all_day:
        start_time = st.time_input("Start time", value=time(9, 0))
        end_time = st.time_input("End time", value=time(10, 0))

    location = st.text_input("Location", max_chars=240)
    notes = st.text_area("Notes", max_chars=10000)

    submitted = st.form_submit_button("Add event")

if submitted:
    try:
        if all_day:
            starts_at = local_datetime(start_date, time.min)
            ends_at = local_datetime(
                end_date + timedelta(days=1), time.min
            )
        else:
            starts_at = local_datetime(start_date, start_time)
            ends_at = local_datetime(end_date, end_time)

        add_event(
            workspace_id=workspace_id,
            title=title,
            starts_at=starts_at,
            ends_at=ends_at,
            all_day=all_day,
            location=location,
            notes=notes,
        )
    except ValueError as error:
        st.warning(str(error))
    except APIError:
        st.error("Supabase could not save this event.")
    except HTTPError:
        st.error(
            "The connection was interrupted. Refresh and check "
            "the calendar before submitting again."
        )
    else:
        st.rerun()
if events:
    st.subheader("Edit an event", anchor=False)

    edit_mode = st.toggle("Edit form", key="edit_calendar_toggle")

    if edit_mode:
        events_by_id = {
            event["id"]: event
            for event in events
        }

        selected_id = st.selectbox(
            "Choose an event",
            options=list(events_by_id),
            format_func=lambda event_id: (
                f"{events_by_id[event_id]['title']} — "
                f"{events_by_id[event_id]['start']:%b %d, %Y}"
            ),
        )

        selected_event = events_by_id[selected_id]

        edit_all_day = st.toggle(
            "All-day event",
            value=selected_event["all_day"],
            key=f"edit_all_day_{selected_id}",
        )

        # All-day events are stored with an exclusive end:
        # midnight immediately after their last included day.
        if selected_event["all_day"]:
            existing_end_date = (
                selected_event["end"] - timedelta(microseconds=1)
            ).date()
            existing_start_time = time(9, 0)
            existing_end_time = time(10, 0)
        else:
            existing_end_date = selected_event["end"].date()
            existing_start_time = selected_event["start"].time()
            existing_end_time = selected_event["end"].time()

        with st.form(f"edit_event_{selected_id}"):
            edit_title = st.text_input(
                "Event title",
                value=selected_event["title"],
                max_chars=160,
            )

            edit_start_date = st.date_input(
                "Start date",
                value=selected_event["start"].date(),
            )

            edit_end_date = st.date_input(
                "End date",
                value=existing_end_date,
                help="For all-day events, choose the last day included.",
            )

            if not edit_all_day:
                edit_start_time = st.time_input(
                    "Start time",
                    value=existing_start_time,
                )
                edit_end_time = st.time_input(
                    "End time",
                    value=existing_end_time,
                )

            edit_location = st.text_input(
                "Location",
                value=selected_event["location"],
                max_chars=240,
            )

            edit_notes = st.text_area(
                "Notes",
                value=selected_event["notes"],
                max_chars=10000,
            )

            save_changes = st.form_submit_button("Save changes")

        if save_changes:
            try:
                if edit_all_day:
                    new_start = local_datetime(
                        edit_start_date, time.min
                    )
                    new_end = local_datetime(
                        edit_end_date + timedelta(days=1),
                        time.min,
                    )
                else:
                    new_start = local_datetime(
                        edit_start_date, edit_start_time
                    )
                    new_end = local_datetime(
                        edit_end_date, edit_end_time
                    )

                save_event(
                    workspace_id=workspace_id,
                    event_id=selected_id,
                    title=edit_title,
                    starts_at=new_start,
                    ends_at=new_end,
                    all_day=edit_all_day,
                    location=edit_location,
                    notes=edit_notes,
                )
            except ValueError as error:
                st.warning(str(error))
            except APIError:
                st.error("Supabase could not save these changes.")
            except HTTPError:
                st.error(
                    "The connection was interrupted. Refresh and "
                    "check the event before submitting again."
                )
            else:
                st.rerun()