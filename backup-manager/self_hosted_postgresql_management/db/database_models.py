import datetime
from typing import Optional
import reflex as rx
from apscheduler.triggers.cron import CronTrigger


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
    schedule: str  # Format: "HH:MM" or cron
    is_active: bool = True

    @property
    def next_run(self) -> Optional[datetime.datetime]:
        """Compute the next run time based on the schedule."""
        if not self.is_active:
            return None
        try:
            now = datetime.datetime.now()
            if len(self.schedule.split(":")) != 2:
                next_run = CronTrigger.from_crontab(self.schedule).get_next_fire_time(None, now)
            else:
                hour, minute = map(int, self.schedule.split(":"))
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += datetime.timedelta(days=1)
                
            return next_run
        except (ValueError, TypeError):
            return None 