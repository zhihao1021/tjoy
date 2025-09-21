from fastapi import HTTPException, status


CREATE_COMMENT_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="An error occurred while creating the comment."
)
