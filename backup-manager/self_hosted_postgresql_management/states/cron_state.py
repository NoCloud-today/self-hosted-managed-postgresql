import asyncio
import datetime

import reflex as rx

from self_hosted_postgresql_management.services.scheduler_service import SchedulerService, ScheduledJob

_scheduler_service = SchedulerService()

class CronState(rx.State):
    cron_jobs_internal: list[ScheduledJob] = []
    is_loading: bool = False
    selected_job_type: str = ""
    selected_schedule_time: str = ""

    @rx.event
    def set_job_type(self, value: str):
        self.selected_job_type = value

    @rx.event
    def set_schedule_time(self, value: str):
        self.selected_schedule_time = value

    @rx.event(background=True)
    async def load_cron_jobs(self):
        async with self:
            self.is_loading = True
            yield
        try:
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
        for job in self.cron_jobs_internal:
            try:
                dt_object = datetime.datetime.fromisoformat(
                    job.next_run
                )
                formatted_time = dt_object.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            except ValueError:
                formatted_time = "Invalid date"
            formatted_jobs.append(
                {
                    "id": job.id,
                    "schedule_expression": job.schedule,
                    "backup_type": job.type.capitalize(),
                    "name": job.name,
                    "next_run_time": formatted_time,
                }
            )
        return formatted_jobs

    @rx.var
    def formatted_next_scheduled_backup(
            self,
    ) -> dict[str, str] | None:
        next_job = self.next_scheduled_backup
        if not next_job:
            return None
        try:
            dt_object = datetime.datetime.fromisoformat(
                next_job.next_run
            )
            formatted_time = dt_object.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except ValueError:
            formatted_time = "Invalid date"
        return {
            "schedule_expression": next_job.schedule,
            "backup_type": next_job.type.capitalize(),
            "description": next_job.name,
            "next_run_time": formatted_time,
        }

    @rx.event(background=True)
    async def create_backup_schedule(self):
        try:
            job_type = self.selected_job_type
            schedule_time = self.selected_schedule_time

            if not job_type or job_type not in ["full", "incr", "diff"]:
                async with self:
                    yield rx.toast.error(f"Invalid backup type selected: {job_type}")
                return

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

            await asyncio.to_thread(
                _scheduler_service.add_backup_job,
                job_type=job_type,
                hour=hour,
                minute=minute
            )
            async with self:
                self.selected_job_type = ""
                self.selected_schedule_time = ""
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
                async with self:
                    yield rx.toast.success("Successfully deleted backup schedule")
                yield CronState.load_cron_jobs
            else:
                async with self:
                    yield rx.toast.error("Failed to delete backup schedule")
        except Exception as e:
            async with self:
                yield rx.toast.error(f"Failed to delete backup schedule: {str(e)}")
