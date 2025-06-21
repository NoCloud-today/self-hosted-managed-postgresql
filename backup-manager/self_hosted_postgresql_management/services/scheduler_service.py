import asyncio
from typing import List
import reflex as rx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from self_hosted_postgresql_management.api.models import ScheduledJob
from self_hosted_postgresql_management.db.database_models import ScheduledBackup
from self_hosted_postgresql_management.services.backup_service import BackupService
from self_hosted_postgresql_management.services.singleton import Singleton
from loguru import logger as log

async def load_cron_jobs():
    log.info("Loading cron jobs")
    with rx.session() as session:
        db_jobs = session.exec(
            ScheduledBackup.select().where(ScheduledBackup.is_active == True)
        ).all()
    scheduler_service = SchedulerService()
    for db_job in db_jobs:
        try:
            hour, minute = map(int, db_job.schedule.split(":"))
            await asyncio.to_thread(
                scheduler_service.add_backup_job,
                job_type=db_job.backup_type,
                hour=hour,
                minute=minute
            )
        except Exception as e:
            log.error(f"Failed to restore job from database: {e}")





class SchedulerService(metaclass=Singleton):
    def __init__(self, backup_service: BackupService = BackupService()):
        self.scheduler = AsyncIOScheduler()
        self.backup_service = backup_service
        self.scheduler.start()

    def add_backup_job(self, job_type: str, hour: int, minute: int) -> ScheduledJob:
        job_id = f"{job_type}_backup_{hour}_{minute}"

        if job_type == "incr":
            job_func = self.backup_service.create_incremental_backup
        elif job_type == "diff":
            job_func = self.backup_service.create_diff_backup
        elif job_type == "full":
            job_func = self.backup_service.create_full_backup
        else:
            raise ValueError(f"Invalid backup type: {job_type}")

        job = self.scheduler.add_job(
            job_func,
            trigger=CronTrigger(hour=hour, minute=minute),
            id=job_id,
            name=f"Daily {job_type} backup at {hour:02d}:{minute:02d}",
            replace_existing=True
        )
        return ScheduledJob(id=job.id,
                            name=job.name,
                            type=job_type,
                            schedule=f"{hour:02d}:{minute:02d}",
                            next_run=job.next_run_time.isoformat() if job.next_run_time else None)

    def get_all_jobs(self) -> List[ScheduledJob]:
        jobs = []
        for job in self.scheduler.get_jobs():
            job_type = job.id.split('_')[0]
            jobs.append(ScheduledJob(id=job.id,
                                     name=job.name,
                                     type=job_type,
                                     schedule=f"{job.trigger.fields[3]}:{job.trigger.fields[4]}",
                                     next_run=job.next_run_time.isoformat() if job.next_run_time else None))
        return jobs

    def remove_job(self, job_id: str) -> bool:
        try:
            self.scheduler.remove_job(job_id)
            return True
        except Exception:
            return False

    def shutdown(self):
        self.scheduler.shutdown()
