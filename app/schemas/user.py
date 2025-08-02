from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    email: EmailStr

class UserLogin(BaseModel):
    username: str
    password: str

class UserInDB(BaseModel):
    id: int
    username: str
    email: EmailStr
    name: str

    class Config:
        orm_mode = True