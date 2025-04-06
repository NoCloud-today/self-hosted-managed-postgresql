from typing import List
from fastapi import APIRouter, HTTPException

from app.src.api.models import Backup
from app.src.api.models import SQLRequest
from app.src.services.backup_service import BackupService

router = APIRouter()
backup_service = BackupService()

@router.post("/backup/incr")
async def create_incremental_backup():
    try:
        result = backup_service.create_incremental_backup()
        return {"message": "Backup created successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup/full")
async def create_full_backup():
    try:
        result = backup_service.create_full_backup()
        return {"message": "Backup created successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup/diff")
async def create_diff_backup():
    try:
        result = backup_service.create_diff_backup()
        return {"message": "Backup created successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backups", response_model=List[Backup])
async def list_backups():
    try:
        return backup_service.list_backups()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore/time")
async def restore_backup(timestamp: int):
    try:
        result = backup_service.restore_backup_by_time(timestamp)
        return {"message": "Restore completed successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore/immediate")
async def restore_immediate(database_name: str = None):
    try:
        result = backup_service.restore_backup_immediate(database_name)
        return {"message": "Restore completed successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database/run")
async def run_sql(request: SQLRequest):
    try:
        result = backup_service.run_sql(request.query, request.database_name)
        return {"message": "SQL executed successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
