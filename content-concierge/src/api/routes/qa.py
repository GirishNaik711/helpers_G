from fastapi import APIRouter

router = APIRouter(tags=["qa"])


@router.post("/sessions/{session_id}/ask")
def ask_placeholder(session_id: str) -> dict:
    # Implemented in later phases.
    return {"session_id": session_id, "detail": "Not implemented yet (Phase 6)."}
