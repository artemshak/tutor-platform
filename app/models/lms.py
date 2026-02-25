import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field, Relationship


class LessonAssignment(SQLModel, table=True):
    __table_args__ = (
        {"postgresql_partition_by": "HASH (teacher_id)"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    teacher_id: uuid.UUID = Field(foreign_key="teacher.id", index=True, primary_key=True, ondelete="CASCADE")
    lesson_id: uuid.UUID = Field(foreign_key="lesson.id", ondelete="CASCADE")
    student_id: uuid.UUID | None = Field(default=None, foreign_key="student.id", index=True, ondelete="CASCADE")
    group_id: uuid.UUID | None = Field(default=None, foreign_key="group.id", index=True)                            # При удалении группу доступ у учеников остаётся

    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    deadline: datetime | None = None


class StepType(str, Enum):
    TEXT = "text"
    VIDEO = "video"
    PDF = "pdf"
    QUIZ = "quiz"


class Folder(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str

    teacher_id: uuid.UUID = Field(foreign_key="teacher.id", index=True)
    parent_id: uuid.UUID | None = Field(default=None, foreign_key="folder.id", ondelete="CASCADE")
    
    lessons: list["Lesson"] | None = Relationship(
        back_populates="folder",
        cascade_delete=True
    )


class Lesson(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: str | None = None
    is_published: bool = Field(default=False, index=True)

    teacher_id: uuid.UUID = Field(foreign_key="teacher.id", index=True)

    folder_id: uuid.UUID | None = Field(default=None, foreign_key="folder.id", ondelete='CASCADE')
    folder: Folder = Relationship(
        back_populates='lessons'
    )
    
    # Храним порядок ID шагов
    steps_order: list[uuid.UUID] = Field(default=[], sa_column=Column(JSONB))
    steps: list["LessonStep"] = Relationship(
        back_populates="lesson",
        cascade_delete=True
    )

    progress: list["LessonProgress"] = Relationship(
        back_populates="lesson",
        cascade_delete=True
    )


class LessonStep(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    type: StepType

    lesson_id: uuid.UUID = Field(foreign_key="lesson.id", ondelete="CASCADE", index=True)
    lesson: Lesson = Relationship(back_populates="steps")
    
    # Содержимое (текст, s3_key для видео/pdf, варианты ответов для квиза)
    # Пример квиза question: {"question": "2+2?", "options": ["3","4"], "correct": "4", "points": 10}
    # Пример квиза input_task: {"input_task": "The coldest _ of the year is _.", "correct": ["season", "winter"], "points": 10}
    # Пример квиза to_correlate: {"to_correlate": [("banana", "cucumber"), ("fruit", "vegetable")], "correct": [("banana", "fruit"), ("cucumber", "vegetable")], "points": 10}
    content: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    

class LessonProgress(SQLModel, table=True):
    """Связь M2M. Здесь фиксируем факт прохождения урока учеником."""
    student_id: uuid.UUID = Field(foreign_key="student.id", primary_key=True)

    lesson_id: uuid.UUID = Field(foreign_key="lesson.id", primary_key=True, ondelete='CASCADE')
    lesson: Lesson = Relationship(back_populates="progress")
    
    is_completed: bool = False
    total_score: int = 0
    
    # Какие шаги пройдены: {"step_id": {"status": "correct", "score": 10}}
    completed_steps: dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    
    completed_at: datetime | None = None
