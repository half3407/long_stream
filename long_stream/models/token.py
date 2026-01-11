from models import user
from pydantic import BaseModel

class TokenData(BaseModel):
    sub: str
    username: str