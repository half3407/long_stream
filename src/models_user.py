# models_user.py
from pydantic import BaseModel

class UserIn(BaseModel):
    username: str
    password: str          # 明文，只活在内存

class UserOut(BaseModel):
    id: int
    username: str          # 返回时不含密码