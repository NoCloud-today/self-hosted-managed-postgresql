import datetime
from typing import Optional
import reflex as rx

class QueryHistory(rx.Model, table=True):
    timestamp_start: datetime.datetime
    timestamp_end: Optional[datetime.datetime]
    operation_type: str
    target: str
    status: str
    message: str
    database_name: str
    sql_query: str

class RestoreHistory(rx.Model, table=True):
    timestamp_start: datetime.datetime
    timestamp_end: Optional[datetime.datetime]
    operation_type: str
    target: str
    status: str
    message: str

class ScheduledBackup(rx.Model, table=True):
    job_id: str
    name: str
    backup_type: str
    schedule: str  # Format: "HH:MM"
    is_active: bool = True

    @property
    def next_run(self) -> Optional[datetime.datetime]:
        """Compute the next run time based on the schedule."""
        if not self.is_active:
            return None
            
        try:
            hour, minute = map(int, self.schedule.split(":"))
            now = datetime.datetime.now()
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If the time has already passed today, schedule for tomorrow
            if next_run <= now:
                next_run += datetime.timedelta(days=1)
                
            return next_run
        except (ValueError, TypeError):
            return None 