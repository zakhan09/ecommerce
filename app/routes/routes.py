from fastapi import APIRouter
from app.routes.v1.auth_routes import router as auth_router
from app.routes.v1.user_routes import router as user_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(user_router, prefix="/users", tags=["Users"]) 