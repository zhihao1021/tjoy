from fastapi import HTTPException, status

CREATE_CONVERSATION_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Failed to create conversation."
)

CONVERSATION_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Conversation not found."
)
