from typing import List

from fastapi import HTTPException, FastAPI
from loguru import logger as log
import reflex as rx
from self_hosted_postgresql_management.api.models import Backup, SQLRequest, ScheduleRequest, ScheduledJob
from self_hosted_postgresql_management.services.backup_service import BackupService
from self_hosted_postgresql_management.services.scheduler_service import SchedulerService

backup_service = BackupService()
scheduler_service = SchedulerService(backup_service)
fastapi_app = FastAPI(title="Backup manager API")


@fastapi_app.post("/backup/incr")
async def create_incremental_backup():
    try:
        log.info("POST /backup/incr")
        backup_service.create_incremental_backup()
        return {"message": "Backup created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.post("/backup/full")
async def create_full_backup():
    try:
        log.info("POST /backup/full")
        backup_service.create_full_backup()
        return {"message": "Backup created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.post("/backup/diff")
async def create_diff_backup():
    try:
        log.info("POST /backup/diff")
        backup_service.create_diff_backup()
        return {"message": "Backup created successfully"}
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.get("/backups", response_model=List[Backup])
async def list_backups():
    try:
        log.info("GET /backups")
        return backup_service.list_backups()
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.post("/restore/time")
async def restore_backup(timestamp: int):
    try:
        log.info("POST /restore/time timestamp={timestamp}")
        backup_service.restore_backup_by_time(timestamp)
        return {"message": "Restore completed successfully"}
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.post("/restore/immediate")
async def restore_immediate(database_name: str = None):
    try:
        log.info("POST /restore/immediate database_name={database_name}")
        backup_service.restore_backup_immediate(database_name)
        return {"message": "Restore completed successfully"}
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.post("/restore/existing")
async def restore_database_from_existing_stanza():
    try:
        log.info("POST /restore/existing")
        backup_service.restore_database_from_existing_stanza()
        return {"message": f"Restore completed successfully"}
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.post("/database/run")
async def run_sql(request: SQLRequest):
    try:
        log.info("POST /database/run {request}")
        result = backup_service.run_sql(request.query, request.database_name)
        return {"message": "SQL executed successfully", "result": result}
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.post("/database")
async def create_database(database_name: str):
    try:
        log.info("POST /database {database_name}")
        backup_service.create_database(database_name)
        return {"message": f"Created database {database_name}"}
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.delete("/database")
async def create_database(database_name: str):
    try:
        log.info(f"DELETE /database {database_name}")
        backup_service.drop_database(database_name)
        return {"message": f"Dropped database {database_name}"}
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.post("/schedule", response_model=ScheduledJob)
async def schedule_backup(request: ScheduleRequest):
    try:
        log.info(f"POST /schedule ${request}")
        return scheduler_service.add_backup_job(request.job_type, request.hour, request.minute)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.get("/schedule", response_model=List[ScheduledJob])
async def list_scheduled_jobs():
    try:
        log.info("GET /schedule query")
        return scheduler_service.get_all_jobs()
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.delete("/schedule/{job_id}")
async def remove_scheduled_job(job_id: str):
    try:
        log.info(f"DELETE /schedule/{job_id}")
        if scheduler_service.remove_job(job_id):
            log.info(f"Removed job {job_id}")
            return {"message": f"Job {job_id} removed successfully"}
        log.error(f"Unable to remove job {job_id} - it does not exist")
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
