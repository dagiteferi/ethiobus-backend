from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app import models, schemas
from app.core.database import get_db
from app.dependencies import get_current_admin
from app.services import report_service

router = APIRouter()

@router.get("/reports/revenue", response_model=schemas.RevenueReport)
async def get_revenue_report(
    report_date: date,
    db: AsyncSession = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    """
    Get a revenue report for a specific date.
    """
    report = await report_service.get_revenue_report(db, report_date)
    return report
