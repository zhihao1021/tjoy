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
    password: str = Field(
        title="Password",
        description="The password for the user account.",
        examples=["strongpassword123"]
    )
