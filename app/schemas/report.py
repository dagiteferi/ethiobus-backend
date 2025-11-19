from pydantic import BaseModel
from typing import List, Dict

class RevenueReport(BaseModel):
    total_revenue: float
    details: Dict[str, float]

class OccupancyReport(BaseModel):
    total_trips: int
    average_occupancy: float
    details: List[Dict]

class TopRoutesReport(BaseModel):
    top_routes: List[Dict]
