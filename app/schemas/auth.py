from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class LoginResponse(BaseModel):
    access_token: str
    id: str
    email: str
    firstName: str | None
    lastName: str | None
    avatar: str | None