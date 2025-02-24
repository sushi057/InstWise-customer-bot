from typing import Optional

from fastapi import Header

from graphs.customer_support.helpers.helpers import get_session_id
from session.session import SessionState

_session_state_cache: dict[tuple[str, str], SessionState] = {}


async def get_session_state(
    org_id_header: str = Header(..., alias="org_id"),
    session_id_header: Optional[str] = Header(..., alias="session_id"),
) -> SessionState:
    """Dependency to get or create a SessionState object for the current session."""

    if session_id_header:
        session_id = session_id_header
    else:
        session_id = get_session_id()

    org_id = org_id_header
    cache_key = (org_id, session_id)

    if cache_key in _session_state_cache:
        print(
            f"SessionState found in cache for session_id: {session_id}, org_id: {org_id}"
        )
        return _session_state_cache[cache_key]
    else:
        new_session_state = SessionState(org_id=org_id, session_id=session_id)
        _session_state_cache[cache_key] = new_session_state

        print(
            f"New SessionState created for session_id: {session_id}, org_id: {org_id}"
        )

        return new_session_state
