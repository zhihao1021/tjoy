from fastapi import HTTPException, status

USER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found."
)

USER_UPDATE_FAILED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User update failed."
)
