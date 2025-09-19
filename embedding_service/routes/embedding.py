from fastapi import FastAPI, Response, status, APIRouter, HTTPException
from contextlib import asynccontextmanager
from embedding_service.src.embedding import ActivityRecommendationSystemGemma
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import SessionDep

router = APIRouter(
    prefix="/embedding",
    tags=["Embedding"]
)

@router.get("/health")
def health_check(response: Response):
    
    is_ready = True

    if is_ready:
        response.status_code = status.HTTP_200_OK
        return {"status": "ok"}
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable"}

@router.get("/parsing/{user_id}")
async def parsing(user_id: int, session: SessionDep):

    sql = text("SELECT id, username, display_name, gender, department FROM users WHERE id = :user_id")
    result = await session.execute(sql, {"user_id": user_id})
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return dict(row._mapping)


recommendation_system = ActivityRecommendationSystemGemma()

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("API starting up...")
    recommendation_system.load_model()
    app.state.recommendation_system = recommendation_system

    yield

    print("API shutting down...")



app = FastAPI(lifespan=lifespan)
app.include_router(router)