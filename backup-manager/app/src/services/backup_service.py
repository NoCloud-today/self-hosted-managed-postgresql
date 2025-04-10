import json
import logging
import subprocess
from datetime import datetime, timezone, timedelta
from typing import List

from app.src.api.models import Backup

log = logging.getLogger(__name__)


class BackupService:
    scripts_directory = "/app/app/scripts"
    @staticmethod
    def _run_command(command: List[str], cwd: str = None) -> str:
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd)
            log.info("Running command: {}".format(command))
            log.info("Output: {}".format(result.stdout))
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Command failed: {e.stderr}")

    @staticmethod
    def _get_formatted_result(unformatted_output: str) -> str:
        start_index = str.find(unformatted_output, "OUTPUT:")
        return unformatted_output[start_index + len("OUTPUT:"):].strip()

    def create_incremental_backup(self) -> str:
        log.info("Creating incremental backup")
        return self._run_command(["./backup_incr.sh"], cwd=self.scripts_directory)

    def create_full_backup(self) -> str:
        log.info("Creating full backup")
        return self._run_command(["./backup_full.sh"], cwd=self.scripts_directory)

    def create_diff_backup(self) -> str:
        log.info("Creating difference backup")
        return self._run_command(["./backup_diff.sh"], cwd=self.scripts_directory)

    def list_backups(self) -> List[Backup]:
        log.info("Getting list of backups")
        result = self._run_command(["./backup_info.sh"], cwd=self.scripts_directory)
        info = json.loads(result)
        if len(info) == 0:
            raise Exception("No backups found")

        backups = []
        for backup in info[0].get("backup", []):
            backups.append(Backup(
                label=backup.get("label", ""),
                timestamp_start=backup.get("timestamp", {}).get("start", 0),
                timestamp_end=backup.get("timestamp", {}).get("end", 0),
                type=backup.get("type", ""),
                size=str(backup.get("info", {}).get("size", ""))
            ))
        return backups

    def restore_backup_by_time(self, timestamp: int) -> str:
        log.info("Restoring backup by time")
        tz_offset = timezone(timedelta(hours=0))
        dt = datetime.fromtimestamp(timestamp, tz_offset)
        iso_time = dt.replace(microsecond=0).isoformat()
        return self._run_command(["./restore_time.sh", iso_time], cwd=self.scripts_directory)

    def restore_backup_immediate(self, database_name: str = None) -> str:
        log.info("Restoring backup immediate")
        command = ["./restore_immediate.sh"]
        if database_name:
            command.append(database_name)
        return self._run_command(command, cwd=self.scripts_directory)

    def run_sql(self, query: str, database_name: str):
        log.info("Running SQL query: '{}' in database {}".format(query, database_name))
        result = self._run_command([
            "./run_sql.sh",
            database_name,
            query
        ], cwd=self.scripts_directory)
        return BackupService._get_formatted_result(result)
