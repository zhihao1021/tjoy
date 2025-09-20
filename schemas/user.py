from pydantic import BaseModel

from typing import Optional


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    gender: Optional[str] = None
    department: Optional[str] = None
    password: Optional[str] = None
    onboarding_year: Optional[int] = None
    onboarding_month: Optional[int] = None
    onboarding_day: Optional[int] = None
    interest: Optional[str] = None
