import uuid
from datetime import datetime, date, timezone
from enum import Enum
from pydantic import model_validator
from sqlmodel import SQLModel, Field, Relationship


class UserRole(str, Enum):
    superuser = "superuser"
    teacher = "teacher"
    student = "student"

class TimestampModel(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc).replace(tzinfo=None)}
    )


class Teacher(TimestampModel, table=True):
    id: uuid.UUID = Field(foreign_key="user.id", primary_key=True, ondelete="CASCADE")
    bio: str | None = None
    experience_years: int = 0
    
    user: 'User' = Relationship(back_populates="teacher_profile")

    students: list['Student'] = Relationship(
        back_populates='teacher',
        cascade_delete=True
    )

class Student(TimestampModel, table=True):
    id: uuid.UUID = Field(foreign_key="user.id", primary_key=True, ondelete="CASCADE")
    points: int = 0
    parent_contact: str | None = None
    
    user: 'User' = Relationship(back_populates="student_profile")

    teacher_id: uuid.UUID = Field(foreign_key="teacher.id", ondelete='CASCADE')
    teacher: Teacher = Relationship(
        back_populates='students'
    )


class User(TimestampModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    
    name: str
    surname: str
    second_name: str | None = None
    birthday: date | None = None
    
    role: UserRole = UserRole.student
    is_active: bool = True
    is_verified: bool = True

    teacher_profile: Teacher | None = Relationship(
        back_populates="user",
        cascade_delete=True
    )
    student_profile: Student | None = Relationship(
        back_populates="user",
        cascade_delete=True
    )

    @model_validator(mode="after")
    def check_profiles(self) -> "User":
        has_teacher = self.teacher_profile is not None
        has_student = self.student_profile is not None

        if self.role == UserRole.superuser:
            if has_teacher or has_student:
                raise ValueError(
                    "Суперпользователь не может иметь профиль студента или преподавателя"
                )
        else:
            if has_teacher == has_student:
                raise ValueError(
                    "Пользователь с ролью должен иметь ровно один профиль: "
                    "либо студента, либо преподавателя"
                )
        return self