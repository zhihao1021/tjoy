from pydantic import BaseModel, Field

from typing import Literal


class Jwt(BaseModel):
    token_type: Literal["Bearer"] = "Bearer"
    access_token: str


class LoginData(BaseModel):
    username: str = Field(
        title="Username",
        description="The unique username of the user.",
        examples=["johndoe"]
    )
    password: str = Field(
        title="Password",
        description="The password for the user account.",
        examples=["strongpassword123"]
    )


class RegisterData(BaseModel):
    username: str = Field(
        title="Username",
        description="The unique username of the user.",
        examples=["johndoe"]
    )
    display_name: str = Field(
        title="Display Name",
        description="The display name of the user.",
        examples=["John Doe"]
    )
    gender: str = Field(
        title="Gender",
        description="The gender of the user.",
        examples=["Female"]
    )
    department: str = Field(
        title="Department",
        description="The department the user belongs to.",
        examples=["Computer Science"]
    )
    onboarding_year: int = Field(
        title="Onboarding Year",
        description="The year the user joined the institution.",
        ge=1900,
        le=2100,
        examples=[2020, 2021, 2022],
    )
    onboarding_month: int = Field(
        title="Onboarding Month",
        description="The month the user joined the institution.",
        ge=1,
        le=12,
        examples=[1, 2, 3],
    )
    onboarding_day: int = Field(
        title="Onboarding Day",
        description="The day the user joined the institution.",
        ge=1,
        le=31,
        examples=[1, 15, 30],
    )
    interest: str = Field(
        default="",
        title="Interest",
        description="The user's interests.",
        examples=["Machine Learning, Data Science"]
    )
    password: str = Field(
        title="Password",
        description="The password for the user account.",
        examples=["strongpassword123"]
    )
