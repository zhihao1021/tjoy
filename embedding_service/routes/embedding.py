from fastapi import FastAPI, Response, status, APIRouter, HTTPException
from contextlib import asynccontextmanager
from embedding_service.src import activity_recommender
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db import async_session
from typing import Dict, Any, Optional
import bcrypt
from pydantic import BaseModel, Field
from snowflake.snowflake import SnowflakeGenerator
from model.user import UserModel
from model.article import ArticleModel 
from rabbitmq_service.sender import send_message
from embedding_service.src.embedding import ActivityRecommendationSystemGemma

router = APIRouter(
    prefix="/embedding",
    tags=["Embedding"]
)

rabbitmq = APIRouter(
    prefix="/rabbitmq",
    tags=["rabbitmq"]
)

@router.post("/rabbitmq_test/{even_id}")
async def rabbitmq_test(event_id:int):
    message = {"event_id": event_id}
    await send_message(message)
    return {"status": "ok", "event_id": event_id}

@router.get("/health")
def health_check(response: Response):
    
    is_ready = True

    if is_ready:
        response.status_code = status.HTTP_200_OK
        return {"status": "ok"}
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable"}

@router.get("/event/{event_id}/recommended_users")
async def get_recommended_users_for_event(event_id: int):

    from db import engine
    async with async_session() as session:
        event_sql = text(
            """
            SELECT a.id,
                   a.title,
                   a.content,
                   a.tags,
                   a.is_event,
                   a.is_public,
                   a.author_visibility,
                   a.author_id,
                   c.name AS category_name
            FROM public.articles a
            LEFT JOIN public.categories c 
                ON a.category_id = c.id
            WHERE a.id = :event_id 
              AND a.is_event = true
            """
        )

        event_result = await session.execute(event_sql, {"event_id": event_id})
        event_row = event_result.fetchone()

        if not event_row:
            raise HTTPException(status_code=404, detail="Event not found")

        event_data = dict(event_row._mapping)

        event_article = ArticleModel(
            id=event_data["id"],
            title=event_data["title"],
            content=event_data["content"],
            tags=event_data["tags"] or "",
            is_event=event_data["is_event"],
            is_public=event_data["is_public"],
            author_visibility=event_data["author_visibility"],
            author_id=event_data["author_id"],
        )
        event_article.category_name = event_data.get("category_name")

        users_sql = text(
            """
            SELECT id, username, display_name, gender, department
            FROM public.users
            ORDER BY id ASC
            """
        )

        users_result = await session.execute(users_sql)
        users_rows = users_result.fetchall()


        from embedding_service.src import activity_recommender
        recommendation_system = activity_recommender
        

        recommendation_system.events_data = {
            f"event_{event_article.id}": event_article
        }

        recommended_users = []
        threshold = 0.02
        total_users = len(users_rows)
        
        print(f"Processing {total_users} users for event {event_id}...")

        for i, user_row in enumerate(users_rows, 1):
            user_data = dict(user_row._mapping)
            user_model = UserModel(**user_data)

            recommendation_system.set_user(user_model)

            try:
                scores = recommendation_system.calculate_comprehensive_score(
                    f"event_{event_article.id}"
                )
                total_score = scores["total_score"]

                if total_score > threshold:
                    recommended_users.append(
                        {
                            "user_id": user_data["id"],
                            "username": user_data["username"],
                            "display_name": user_data["display_name"],
                            "total_score": round(total_score, 4),
                            "score_breakdown": {
                                "content_similarity": round(
                                    scores.get("content_similarity", 0), 4
                                ),
                                "tag_similarity": round(
                                    scores.get("tag_similarity", 0), 4
                                ),
                                "board_similarity": round(
                                    scores.get("board_similarity", 0), 4
                                ),
                                "behavioral_similarity": round(
                                    scores.get("behavioral_similarity", 0), 4
                                ),
                                "search_relevance": round(
                                    scores.get("search_relevance", 0), 4
                                ),
                            },
                        }
                    )
                    print(f"  ✓ User {user_data['id']} ({user_data['username']}): score {total_score:.4f}")
                
                if i % 10 == 0 or i == total_users:
                    print(f"  Progress: {i}/{total_users} users processed")
                    
            except Exception as e:
                print(f"  ✗ User {user_data['id']} error: {e}")
                continue

        recommended_users.sort(key=lambda x: x["total_score"], reverse=True)
        return {
            "event_id": event_id,
            "event_title": event_data["title"],
            "threshold": threshold,
            "recommended_users": recommended_users,
            "total_recommended_users": len(recommended_users),
        }

@router.get("/parsing/{user_id}")
async def parsing(user_id: int):
    from db import engine

    async with AsyncSession(engine) as session:
        user_sql = text(
            """
            SELECT id, username, display_name, gender, department
            FROM users
            WHERE id = :user_id
            """
        )
        user_result = await session.execute(user_sql, {"user_id": user_id})
        user_row = user_result.fetchone()

        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = dict(user_row._mapping)
        user_model = UserModel(**user_data)
        activity_recommender.set_user(user_model)
        events_sql = text(
            """
            SELECT a.id,
                   a.title,
                   a.content,
                   a.tags,
                   a.is_event,
                   a.is_public,
                   a.author_visibility,
                   c.name AS category_name
            FROM public.articles a
            LEFT JOIN public.categories c
                   ON a.category_id = c.id
            WHERE a.is_event = TRUE
            ORDER BY a.id ASC
            """
        )

        events_result = await session.execute(events_sql)
        events_rows = events_result.fetchall()

        from model.article import ArticleModel

        for row in events_rows:
            event_data = dict(row._mapping)

            article = ArticleModel(
                id=event_data["id"],
                title=event_data["title"],
                content=event_data["content"],
                tags=event_data["tags"] or "",
                is_event=event_data["is_event"],
                is_public=event_data["is_public"],
                author_visibility=event_data["author_visibility"],
                author=user_model, 
            )
            article.category_name = event_data.get("category_name")
            activity_recommender.add_event_data(f"event_{article.id}", article)

        print(events_rows)

        recommended_events = activity_recommender.recommend_events()
        event_list = []
        for event in recommended_events:
            event_dict = {
                "id": event.id,
                "title": event.title,
                "content": event.content,
                "tags": event.tags,
                "category": getattr(event, "category_name", None),
                "author": event.author.display_name if event.author else None,
            }
            event_list.append(event_dict)

        return {
            "user_id": user_data["id"],
            "username": user_data["username"],
            "display_name": user_data["display_name"],
            "gender": user_data["gender"],
            "department": user_data["department"],
            "recommended_events": event_list,
            "total_recommendations": len(event_list),
        }




@asynccontextmanager
async def lifespan(app:FastAPI):
    print("API starting up...")
    from embedding_service.src import activity_recommender
    app.state.recommendation_system = activity_recommender

    yield

    print("API shutting down...")



app = FastAPI(lifespan=lifespan)
app.include_router(router)