import datetime
from typing import Optional
from pydantic import BaseModel


class Observation(BaseModel):
    utility: str
    start: Optional[datetime.date] = None
    end: Optional[datetime.date] = None
