import datetime
from typing import Optional
from pydantic import BaseModel


class Report(BaseModel):
    # user-submitted request
    utility: str
    start: Optional[datetime.date] = None
    end: Optional[datetime.date] = None
