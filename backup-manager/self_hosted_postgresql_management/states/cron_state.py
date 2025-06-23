import asyncio
import datetime

import reflex as rx

from self_hosted_postgresql_management.services.scheduler_service import SchedulerService, ScheduledJob
from self_hosted_postgresql_management.db.database_models import ScheduledBackup
from loguru import logger as log

_scheduler_service = SchedulerService()

class CronState(rx.State):
    cron_jobs_internal: list[ScheduledJob] = []
    is_loading: bool = False
    selected_job_type: str = ""
    selected_schedule_time: str = ""
    use_cron_expression: bool = False
    cron_expression: str = ""

    @rx.event
    def set_job_type(self, value: str):
        self.selected_job_type = value

    @rx.event
    def set_schedule_time(self, value: str):
        self.selected_schedule_time = value

    @rx.event
    def toggle_schedule_type(self):
        self.use_cron_expression = not self.use_cron_expression
        self.selected_schedule_time = ""
        self.cron_expression = ""

    @rx.event
    def set_cron_expression(self, value: str):
        self.cron_expression = value

    @rx.event(background=True)
    async def load_cron_jobs(self):
        async with self:
            self.is_loading = True
            yield
        try:
            with rx.session() as session:
                db_jobs = session.exec(
                    ScheduledBackup.select().where(ScheduledBackup.is_active == True)
                ).all()
                
                for db_job in db_jobs:
                    try:
                        if len(db_job.schedule.split(":")) != 2:
                            await asyncio.to_thread(_scheduler_service.add_backup_job_by_cron,
                                                    job_type=db_job.backup_type,
                                                    cron=db_job.schedule)
                        else:
                            hour, minute = map(int, db_job.schedule.split(":"))
                            await asyncio.to_thread(
                                _scheduler_service.add_backup_job,
                                job_type=db_job.backup_type,
                                hour=hour,
                                minute=minute
                            )
                    except Exception as e:
                        log.error(f"Failed to restore job from database: {e}")

            jobs = await asyncio.to_thread(
                _scheduler_service.get_all_jobs
            )
            async with self:
                self.cron_jobs_internal = jobs
                yield
        except Exception as e:
            async with self:
                yield rx.toast.error(
                    f"Failed to load cron jobs: {str(e)}"
                )
        finally:
            async with self:
                self.is_loading = False
                yield

    @rx.event(background=True)
    async def create_backup_schedule(self):
        try:
            job_type = self.selected_job_type
            schedule_time = self.selected_schedule_time
            cron_expr = self.cron_expression

            if not job_type or job_type not in ["full", "incr", "diff"]:
                async with self:
                    yield rx.toast.error(f"Invalid backup type selected: {job_type}")
                return

            if self.use_cron_expression:
                if not cron_expr:
                    async with self:
                        yield rx.toast.error("Please enter a cron expression")
                    return
                
                try:
                    job = await asyncio.to_thread(
                        _scheduler_service.add_backup_job_by_cron,
                        job_type=job_type,
                        cron=cron_expr
                    )
                except ValueError as e:
                    async with self:
                        yield rx.toast.error(f"Invalid cron expression: {str(e)}")
                    return
            else:
                if not schedule_time:
                    async with self:
                        yield rx.toast.error("Please select a schedule time")
                    return

                try:
                    hour, minute = map(int, schedule_time.split(":"))
                except ValueError:
                    async with self:
                        yield rx.toast.error("Invalid time format")
                    return

                if not (0 <= hour <= 23):
                    async with self:
                        yield rx.toast.error("Hour must be between 0 and 23")
                    return

                if not (0 <= minute <= 59):
                    async with self:
                        yield rx.toast.error("Minute must be between 0 and 59")
                    return

                job = await asyncio.to_thread(
                    _scheduler_service.add_backup_job,
                    job_type=job_type,
                    hour=hour,
                    minute=minute
                )
            
            with rx.session() as session:
                db_job = ScheduledBackup(
                    job_id=job.id,
                    name=job.name,
                    backup_type=job.type,
                    schedule=job.schedule,
                    is_active=True
                )
                session.add(db_job)
                session.commit()

            async with self:
                self.selected_job_type = ""
                self.selected_schedule_time = ""
                self.cron_expression = ""
                yield rx.toast.success(f"Successfully created {job_type} backup schedule")
            yield CronState.load_cron_jobs
        except Exception as e:
            async with self:
                yield rx.toast.error(f"Failed to create backup schedule: {str(e)}")

    @rx.event(background=True)
    async def delete_backup_schedule(self, job_id: str):
        try:
            success = await asyncio.to_thread(
                _scheduler_service.remove_job,
                job_id=job_id
            )
            if success:
                with rx.session() as session:
                    db_job = session.exec(
                        ScheduledBackup.select().where(ScheduledBackup.job_id == job_id)
                    ).first()
                    if db_job:
                        db_job.is_active = False
                        session.commit()
                
                async with self:
                    yield rx.toast.success("Successfully deleted backup schedule")
                yield CronState.load_cron_jobs
            else:
                async with self:
                    yield rx.toast.error("Failed to delete backup schedule")
        except Exception as e:
            async with self:
                yield rx.toast.error(f"Failed to delete backup schedule: {str(e)}")

    @rx.var
    def cron_jobs(self) -> list[ScheduledJob]:
        return self.cron_jobs_internal

    @rx.var
    def sorted_cron_jobs(self) -> list[ScheduledJob]:
        return self.cron_jobs_internal

    @rx.var
    def next_scheduled_backup(self) -> ScheduledJob | None:
        if not self.sorted_cron_jobs:
            return None
        return self.sorted_cron_jobs[0]

    @rx.var
    def formatted_cron_jobs(self) -> list[dict[str, str]]:
        formatted_jobs = []
        with rx.session() as session:
            for job in self.cron_jobs_internal:
                db_job = session.exec(
                    ScheduledBackup.select().where(ScheduledBackup.job_id == job.id)
                ).first()
                
                next_run_time = "Invalid date"
                if db_job and db_job.next_run:
                    next_run_time = db_job.next_run.strftime("%Y-%m-%d %H:%M:%S")
                
                formatted_jobs.append(
                    {
                        "id": job.id,
                        "schedule_expression": job.schedule,
                        "backup_type": job.type.capitalize(),
                        "name": job.name,
                        "next_run_time": next_run_time,
                    }
                )
        return formatted_jobs

    @rx.var
    def formatted_next_scheduled_backup(self) -> dict[str, str] | None:
        next_job = self.next_scheduled_backup
        if not next_job:
            return None
            
        with rx.session() as session:
            db_job = session.exec(
                ScheduledBackup.select().where(ScheduledBackup.job_id == next_job.id)
            ).first()
            
            next_run_time = "Invalid date"
            if db_job and db_job.next_run:
                next_run_time = db_job.next_run.strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "schedule_expression": next_job.schedule,
                "backup_type": next_job.type.capitalize(),
                "description": next_job.name,
                "next_run_time": next_run_time,
            }
