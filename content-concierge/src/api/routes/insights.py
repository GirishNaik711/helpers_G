from fastapi import APIRouter

router = APIRouter(tags=["insights"])

@router.post("/insights")
def generate_insights_placeholder() -> dict:
    
    #placeholder
    
    return {"detail": "Not implemented yet"}

