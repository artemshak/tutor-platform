import uuid
from datetime import date
from pydantic import BaseModel, EmailStr


# Base schemas for users
class UserBase(BaseModel):
    email: EmailStr

    name: str
    surname: str
    second_name: str | None = None
    birthday: date | None = None


class TeacherProfileBase(BaseModel):
    bio: str | None = None
    experience_years: int = 0


class StudentProfileBase(BaseModel):
    parent_contact: str | None = None
    teacher_id: uuid.UUID