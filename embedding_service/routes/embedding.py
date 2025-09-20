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

@router.post("/adduser")
async def add_user(user_data: UserCreateRequest):
    """
    接收 JSON 格式的使用者資料並插入資料庫
    """
    
    # 對密碼進行 hash 處理
    password = user_data.password.encode('utf-8')
    password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
    
    # 生成 Snowflake ID
    snowflake_gen = SnowflakeGenerator(instance_id=0)
    new_id = snowflake_gen.next_id().value
    
    sql = text("""
        INSERT INTO users (id, username, display_name, gender, department, password_hash)
        VALUES (:id, :username, :display_name, :gender, :department, :password_hash)
        RETURNING id
    """)
    
    # 直接使用 engine 創建 session
    from db import engine
    async with AsyncSession(engine) as session:
        try:
            # 先檢查 username 是否已存在
            check_sql = text("SELECT id FROM users WHERE username = :username")
            existing_user = await session.execute(check_sql, {"username": user_data.username})
            if existing_user.fetchone():
                raise HTTPException(status_code=409, detail=f"Username '{user_data.username}' already exists")
            
            result = await session.execute(sql, {
                "id": new_id,
                "username": user_data.username,
                "display_name": user_data.display_name,
                "gender": user_data.gender,
                "department": user_data.department,
                "password_hash": password_hash
            })
            new_id = result.scalar_one()
            await session.commit()
            print(f"Successfully inserted user with ID: {new_id}")
        except HTTPException:
            # 重新拋出 HTTPException
            await session.rollback()
            raise
        except Exception as e:
            print(f"Database error: {str(e)}")
            print(f"Error type: {type(e)}")
            await session.rollback()
            raise HTTPException(status_code=400, detail=f"Insert failed: {str(e)}")

    return {"status": "success", "id": new_id, "username": user_data.username}

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