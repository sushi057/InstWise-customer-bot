from typing import Literal, Optional, cast

from fastapi import Header

from graphs.customer_support.helpers.helpers import get_session_id
from session.session import PrivateSession, PublicSession, TaskSession
from session.session_base import SessionState

_session_state_cache: dict[
    tuple[str, str], SessionState | PrivateSession | PublicSession | TaskSession
] = {}


async def get_session_state_core(
    org_id_header: str = Header(..., alias="org_id"),
    session_id_header: Optional[str] = Header(None, alias="session_id"),
    session_type: Optional[Literal["private", "public", "task"]] = "private",
    *,
    task_name: Optional[str] = None,
) -> PrivateSession | PublicSession | TaskSession | SessionState:
    """Dependency to get or create a SessionState object for the current session."""

    if not session_id_header:
        session_id_header = get_session_id()

    org_id = org_id_header
    session_id = session_id_header
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
        elif task_name == "task":
            new_session_state = TaskSession(org_id, session_id, task_name)
        else:
            new_session_state = SessionState(org_id, session_id)

        _session_state_cache[cache_key] = new_session_state

        print(
            f"New SessionState created for session_id: {session_id}, org_id: {org_id}"
        )

        return new_session_state


async def get_private_session_state(
    org_id_header: str = Header(..., alias="org_id"),
    session_id_header: Optional[str] = Header(None, alias="session_id"),
) -> PrivateSession:
    """Dependency to get or create a PrivateSession object for the current session."""

    session_state = await get_session_state_core(
        org_id_header=org_id_header,
        session_id_header=session_id_header,
        session_type="private",
    )

    return cast(PrivateSession, session_state)


async def get_public_session_state(
    org_id_header: str = Header(..., alias="org_id"),
    session_id_header: Optional[str] = Header(None, alias="session_id"),
) -> PublicSession:
    """Dependency to get or create a PublicSession object for the current session."""

    session_state = await get_session_state_core(
        org_id_header=org_id_header,
        session_id_header=session_id_header,
        session_type="public",
    )

    return cast(PublicSession, session_state)


async def get_task_session_state(
    org_id_header: str = Header(..., alias="org_id"),
    session_id_header: Optional[str] = Header(None, alias="session_id"),
    task_name: str = Header(..., alias="task_name"),
) -> TaskSession:
    """Dependency to get or create a TaskSession object for the current session."""

    session_state = await get_session_state_core(
        org_id_header=org_id_header,
        session_id_header=session_id_header,
        session_type="task",
        task_name=task_name,
    )

    return cast(TaskSession, session_state)
