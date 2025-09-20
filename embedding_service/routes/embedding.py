from fastapi import FastAPI, Response, status, APIRouter, HTTPException
from contextlib import asynccontextmanager
from embedding_service.src.embedding import ActivityRecommendationSystemGemma
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db import SessionDep
from typing import Dict, Any, Optional
import bcrypt
from pydantic import BaseModel, Field
from snowflake.snowflake import SnowflakeGenerator

class UserCreateRequest(BaseModel):
    username: str = Field(..., example="newuser123", description="使用者名稱 (必須唯一)")
    display_name: str = Field(..., example="測試使用者", description="顯示名稱")
    gender: str = Field(..., example="Male", description="性別 (Male/Female/Other)")
    department: str = Field(..., example="Engineering", description="部門名稱")
    password: str = Field(..., example="testpassword123", description="原始密碼 (將自動進行 hash 處理)")

# 172.16.2.12

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
async def parsing(user_id: int):

    sql = text("SELECT id, username, display_name, gender, department FROM users WHERE id = :user_id")
    
    # 直接使用 engine 創建 session
    from db import engine
    async with AsyncSession(engine) as session:
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