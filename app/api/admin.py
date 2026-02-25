from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.user import Teacher, User, UserRole
from app.core.security import role_required, get_password_hash, validate_unique_email
from app.core.database import get_session
from app.schemas.auth import TeacherCreate
from app.core.templates import templates


router = APIRouter()


@router.get("/create-teacher", response_class=HTMLResponse)
async def get_create_teacher_page(request: Request, _ = Depends(role_required([UserRole.superuser]))):
    return templates.TemplateResponse("create_teacher.html", {"request": request})


@router.post("/create-teacher")
async def create_teacher(
    user_data: Annotated[TeacherCreate, Depends(validate_unique_email)],
    session: AsyncSession = Depends(get_session),
    _ = Depends(role_required([UserRole.superuser])) # Only superuser
):
    
    new_user = User(
        **user_data.model_dump(exclude={"password"}),
        password_hash=get_password_hash(user_data.password),
        role=UserRole.teacher
    )

    session.add(new_user)
    await session.flush()

    new_teacher = Teacher(
        id=new_user.id,
        bio=user_data.profile.bio,
        experience_years=user_data.profile.experience_years
    )

    session.add(new_teacher)
    await session.commit()

    return {"message": "Учитель успешно создан",
            "email": user_data.email
            }
