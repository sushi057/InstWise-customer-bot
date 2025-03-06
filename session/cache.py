from typing import Literal, Optional, cast

from graphs.customer_support.helpers.helpers import get_session_id
from session.session import PrivateSession, PublicSession, TaskSession
from session.session_base import SessionState

_session_state_cache: dict[
    tuple[str, str], SessionState | PrivateSession | PublicSession | TaskSession
] = {}


async def get_session_state_core(
    org_id: str,
    session_id: Optional[str] = None,
    session_type: Optional[Literal["private", "public", "task"]] = "private",
    *,
    task_name: Optional[str] = None,
) -> PrivateSession | PublicSession | TaskSession | SessionState:
    """Dependency to get or create a SessionState object for the current session."""

    if not session_id:
        session_id = get_session_id()

    org_id = org_id
    session_id = session_id
    cache_key = (org_id, session_id)

    if cache_key in _session_state_cache:
        print(
            f"SessionState found in cache for session_id: {session_id}, org_id: {org_id}"
        )
        return _session_state_cache[cache_key]
    else:
        if session_type == "private":
            new_session_state = PrivateSession(org_id, session_id)
        elif session_type == "public":
            new_session_state = PublicSession(org_id, session_id)
        elif session_type == "task":
            new_session_state = TaskSession(org_id, session_id, task_name)
        else:
            new_session_state = SessionState(org_id, session_id)

        _session_state_cache[cache_key] = new_session_state

        print(
            f"New SessionState created for session_id: {session_id}, org_id: {org_id}"
        )

        return new_session_state


async def get_private_session_state(
    org_id: str,
    session_id: Optional[str] = None,
) -> PrivateSession:
    """Dependency to get or create a PrivateSession object for the current session."""

    session_state = await get_session_state_core(
        org_id=org_id,
        session_id=session_id,
        session_type="private",
    )

    return cast(PrivateSession, session_state)


async def get_public_session_state(
    org_id: str,
    session_id: Optional[str] = None,
) -> PublicSession:
    """Dependency to get or create a PublicSession object for the current session."""

    session_state = await get_session_state_core(
        org_id=org_id,
        session_id=session_id,
        session_type="public",
    )

    return cast(PublicSession, session_state)


async def get_task_session_state(
    org_id: str,
    task_name: str,
    session_id: Optional[str] = None,
) -> TaskSession:
    """Dependency to get or create a TaskSession object for the current session."""

    session_state = await get_session_state_core(
        org_id=org_id,
        session_id=session_id,
        session_type="task",
        task_name=task_name,
    )

    return cast(TaskSession, session_state)
