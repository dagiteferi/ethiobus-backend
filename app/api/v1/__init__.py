from fastapi import APIRouter

from . import auth, passenger, driver, admin, reports

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(passenger.router, prefix="/passenger", tags=["passenger"])
api_router.include_router(driver.router, prefix="/driver", tags=["driver"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(reports.router, prefix="/admin", tags=["admin-reports"]) # As per spec
