from dataclasses import dataclass
from typing import Optional

@dataclass
class Backup:
    label: str
    timestamp_start: int
    timestamp_end: int
    type: str
    size: str
    status: str

@dataclass
class SQLRequest:
    query: str
    database_name: str

@dataclass
class ScheduleRequest:
    job_type: str
    hour: int
    minute: int

@dataclass
class ScheduledJob:
    id: str
    name: str
    type: str
    schedule: str
    next_run: Optional[str]