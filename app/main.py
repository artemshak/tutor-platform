from fastapi import FastAPI

from app.core.security import JWTCookieMiddleware

from app.api.auth import router as auth_router
from app.api.admin import router as admin_router


app = FastAPI()

# Middleware
app.add_middleware(JWTCookieMiddleware)

# Router
app.include_router(auth_router, prefix='/auth')
app.include_router(admin_router, prefix='/superuser')