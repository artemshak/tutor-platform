from datetime import datetime, timedelta, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from pwdlib import PasswordHash
import jwt

from app.core.config import settings
from app.models.user import UserRole, User
from app.schemas.auth import UserCreate, TeacherCreate, StudentCreate
from app.core.database import get_session


# Password
password_hash = PasswordHash.recommended()


def verify_password(blank_password, hashed_password):
    return password_hash.verify(blank_password, hashed_password)


def get_password_hash(blank_password):
    return password_hash.hash(blank_password)


# JWT
def create_access_token(email: str, role: str):
    payload = {
        "sub": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


# Role check
def role_required(allowed_roles: list[UserRole]):
    def decorator(request: Request):
        user_role = getattr(request.state, "user_role", None)
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Недостаточно прав"
            )
        return user_role
    return decorator


# Email verification for uniqueness
async def validate_unique_email(
    user_data: UserCreate | TeacherCreate | StudentCreate, 
    session: AsyncSession = Depends(get_session)
    ) -> UserCreate:

    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с такой почтой уже зарегистрирован"
        )
    
    return user_data


# Security Middleware
class JWTCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token_cookie = request.cookies.get("access_token")
        is_login_page = request.url.path == "/auth/login"

        user_authenticated = False
        if token_cookie:
            try:
                print('*****', token_cookie)
                token = token_cookie.replace("Bearer ", "")
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                request.state.user_email = payload.get("sub")
                request.state.user_role = payload.get("role")
                user_authenticated = True
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                user_authenticated = False
                
        print('*****', user_authenticated)
        if user_authenticated and is_login_page:
            return RedirectResponse(url="/dashboard")

        if request.url.path in settings.EXCLUDED_PATHS:
            return await call_next(request)

        if not user_authenticated:
            if "text/html" in request.headers.get("accept", ""):
                return RedirectResponse(url="/auth/login")
            
            return JSONResponse(
                status_code=401, 
                content={"detail": "Войдите в аккаунт!!!"}
            )

        return await call_next(request)
