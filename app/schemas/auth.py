from pydantic import Field, field_validator
import re

from app.schemas.user import UserBase, TeacherProfileBase, StudentProfileBase


# User schemes for creation
class UserCreate(UserBase):
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if re.search(r"[а-яА-ЯёЁ]", v):
            raise ValueError("Пароль не должен содержать русские буквы")
        
        if len(v) < 8:
            raise ValueError("Пароль должен быть не менее 8 символов")
        
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную латинскую букву")
            
        if not re.search(r"[0-9]", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
            
        if not re.search(r"\W", v):
            raise ValueError("Пароль должен содержать хотя бы один спецсимвол")
            
        return v


class TeacherCreate(UserCreate):
    profile: TeacherProfileBase


class StudentCreate(UserCreate):
    profile: StudentProfileBase


class AdminCreate(UserCreate):
    pass