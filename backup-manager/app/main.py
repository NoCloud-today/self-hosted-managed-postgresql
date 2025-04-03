import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List

from fastapi import FastAPI, HTTPException

app = FastAPI()


@dataclass
class Backup:
    label: str
    timestamp: int
    type: str
    size: str

@dataclass
class SQLRequest:
    query: str
    database_name: str = "postgres"

def run_command(command: List[str], cwd: str = None) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command failed: {e.stderr}")


@app.post("/backup/incr")
async def create_incremental_backup():
    try:
        result = run_command(["/app/scripts/backup_incr.sh"], cwd="/app/scripts")
        return {"message": "Backup created successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backup/full")
async def create_full_backup():
    try:
        result = run_command(["/app/scripts/backup_full.sh"], cwd="/app/scripts")
        return {"message": "Backup created successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backup/diff")
async def create_diff_backup():
    try:
        result = run_command(["/app/scripts/backup_diff.sh"], cwd="/app/scripts")
        return {"message": "Backup created successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/backups", response_model=List[Backup])
async def list_backups():
    try:
        result = run_command(["/app/scripts/backup_info.sh"], cwd="/app/scripts")
        info = json.loads(result)
        if len(info) == 0:
            raise HTTPException(status_code=404, detail="No backups found")
        backups = []
        for backup in info[0].get("backup", []):
            backups.append(Backup(
                label=backup.get("label", ""),
                timestamp=backup.get("timestamp", {}).get("start", 0),
                type=backup.get("type", ""),
                size=str(backup.get("info", {}).get("size", ""))
            ))
        return backups
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/restore/time")
async def restore_backup(timestamp: int):
    try:
        tz_offset = timezone(timedelta(hours=0))
        dt = datetime.fromtimestamp(timestamp, tz_offset)
        iso_time = dt.replace(microsecond=0).isoformat()
        result = run_command([
            "/app/scripts/restore_time.sh",
            iso_time
        ], cwd="/app/scripts")
        return {"message": "Restore completed successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/restore/immediate")
async def restore_immediate(database_name: str = None):
    try:
        if database_name is None:
            result = run_command(["/app/scripts/restore_immediate.sh"], cwd="/app/scripts")
        else:
            result = run_command(["/app/scripts/restore_immediate.sh", database_name], cwd="/app/scripts")
        return {"message": "Restore completed successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/database/run")
async def run_sql(request: SQLRequest):
    try:
        result = run_command([
            "/app/scripts/run_sql.sh",
            request.database_name,
            request.query
        ], cwd="/app/scripts")
        return {"message": "SQL executed successfully", "result": get_formatted_result(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_formatted_result(unformatted_output: str) -> str:
    start_index = str.find(unformatted_output, "OUTPUT:")
    return unformatted_output[start_index + len("OUTPUT:"):].strip()