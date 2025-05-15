from typing import List, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job
from app.src.services.backup_service import BackupService

class SchedulerService:
    def __init__(self, backup_service: BackupService):
        self.scheduler = AsyncIOScheduler()
        self.backup_service = backup_service
        self.scheduler.start()

    def add_backup_job(self, job_type: str, hour: int, minute: int) -> Dict[str, Any]:
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

        return {
            "id": job.id,
            "name": job.name,
            "type": job_type,
            "schedule": f"{hour:02d}:{minute:02d}",
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None
        }

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        jobs = []
        for job in self.scheduler.get_jobs():
            job_type = job.id.split('_')[0]
            jobs.append({
                "id": job.id,
                "name": job.name,
                "type": job_type,
                "schedule": f"{job.trigger.fields[3]}:{job.trigger.fields[4]}",
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            })
        return jobs

    def remove_job(self, job_id: str) -> bool:
        try:
            self.scheduler.remove_job(job_id)
            return True
        except Exception:
            return False

    def shutdown(self):
        self.scheduler.shutdown() 