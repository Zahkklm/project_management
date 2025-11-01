from pydantic import BaseModel, Field, field_validator


LOGIN_REGEX = r"^[a-zA-Z0-9_.-]+$"


class UserCreate(BaseModel):
    login: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=LOGIN_REGEX,
        example="johndoe",
    )
    password: str = Field(
        ..., min_length=6, max_length=128, example="strongpassword"
    )
    repeat_password: str = Field(
        ..., min_length=6, max_length=128, example="strongpassword"
    )

    @field_validator("repeat_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("passwords do not match")
        return v


class UserLogin(BaseModel):
    login: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=LOGIN_REGEX,
        example="johndoe",
    )
    password: str = Field(
        ..., min_length=6, max_length=128, example="strongpassword"
    )


class UserResponse(BaseModel):
    id: int = Field(..., ge=1, example=1)
    login: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=LOGIN_REGEX,
        example="johndoe",
    )

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
