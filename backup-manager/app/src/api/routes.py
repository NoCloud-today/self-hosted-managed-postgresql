from typing import List
from fastapi import APIRouter, HTTPException

from app.src.api.models import Backup
from app.src.api.models import SQLRequest
from app.src.services.backup_service import BackupService

router = APIRouter()
backup_service = BackupService()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/backup/incr")
async def create_incremental_backup():
    try:
        backup_service.create_incremental_backup()
        return {"message": "Backup created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup/full")
async def create_full_backup():
    try:
        backup_service.create_full_backup()
        return {"message": "Backup created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup/diff")
async def create_diff_backup():
    try:
        backup_service.create_diff_backup()
        return {"message": "Backup created successfully"}
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
        backup_service.restore_backup_by_time(timestamp)
        return {"message": "Restore completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore/immediate")
async def restore_immediate(database_name: str = None):
    try:
        backup_service.restore_backup_immediate(database_name)
        return {"message": "Restore completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore/existing")
async def restore_database_from_existing_stanza():
    try:
        backup_service.restore_database_from_existing_stanza()
        return {"message": f"Restore completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database/run")
async def run_sql(request: SQLRequest):
    try:
        result = backup_service.run_sql(request.query, request.database_name)
        return {"message": "SQL executed successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database/")
async def create_database(database_name: str):
    try:
        backup_service.create_database(database_name)
        return {"message": f"Created database {database_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/database/")
async def create_database(database_name: str):
    try:
        backup_service.drop_database(database_name)
        return {"message": f"Dropped database {database_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))