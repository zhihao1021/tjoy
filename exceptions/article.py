from fastapi import HTTPException, status


CREATE_ARTICLE_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Failed to create article."
)
