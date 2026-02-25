from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, status, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_session
from sqlmodel import select
from ..models.user import User

from ..core.security import verify_password, create_access_token
from ..core.config import settings

from app.core.templates import templates


router = APIRouter()


@router.get('/login', response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})



@router.post('/login')
async def login(response: Response, 
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                session: Annotated[AsyncSession, Depends(get_session)]):
    
    statement = select(User).where(User.email == form_data.username)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if user is None: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Неверная почта или пароль. Проверь ещё раз :)')
    
    if not verify_password(form_data.password, user.password_hash): 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Неверная почта или пароль. Проверь ещё раз :)')
    
    token = create_access_token(email=user.email, role=user.role)
    
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {token}",
        path='/',
        httponly=True,     # Защита от XSS
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES*60,      # Время жизни в секундах
        samesite="lax",    # Защита от CSRF умеренная 
        secure=False       # для HTTPS
    )
    return {"status": "ok", "message": "Успешный вход"}