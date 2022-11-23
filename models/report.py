from datetime import date, timedelta
from typing import Optional
from pydantic import BaseModel


class Report(BaseModel):
    # user-submitted request
    utility: str = "Metro WW - Platte/Central"
    start: Optional[date] = date.today() - timedelta(days=30)
    end: Optional[date] = date.today()
