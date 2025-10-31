from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    repeat_password: str = Field(..., min_length=6)

    @field_validator("repeat_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("passwords do not match")
        return v


class UserLogin(BaseModel):
    login: str
    password: str


class UserResponse(BaseModel):
    id: int
    login: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
