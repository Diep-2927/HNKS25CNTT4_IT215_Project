from pydantic import BaseModel

class Token(BaseModel):
    """Dữ liệu trả về cho client sau khi login thành công"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Dữ liệu trích xuất từ JWT payload để validate"""
    email: str | None = None