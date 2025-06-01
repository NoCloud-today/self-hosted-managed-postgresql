import json
import subprocess
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple

import psycopg2
from loguru import logger as log
from psycopg2 import sql

from self_hosted_postgresql_management.api.models import Backup
from self_hosted_postgresql_management.services.singleton import Singleton


class BackupService(metaclass=Singleton):
    def __init__(self, db_params: Optional[Dict[str, Any]] = None):
        self.db_params = db_params or {
            "dbname": "postgres",
            "user": "postgres",
            "password": "postgres",
            "host": "pg",
            "port": "5432"
        }

    scripts_directory = "/app/scripts"

    @staticmethod
    def _run_command(command: List[str], cwd: str = None) -> str:
        result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
        log.info("Running command: {}".format(command))
        log.info("Output: {}".format(result.stdout))
        if result.returncode == 0:
            return result.stdout
        raise Exception(f"Command failed: {result.stderr}")

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
        try:
            info = json.loads(result)
        except Exception as e:
            log.exception(f"Error parsing backup info {e}")
            raise e
        if len(info) == 0:
            raise Exception("No backups found")

        backups = []
        for backup in info[0].get("backup", []):
            error = backup.get("error", False)
            status = "Success"
            if error:
                status = "Failure"
            backups.append(Backup(
                label=backup.get("label", ""),
                timestamp_start=backup.get("timestamp", {}).get("start", 0),
                timestamp_end=backup.get("timestamp", {}).get("stop", 0),
                type=backup.get("type", ""),
                size=str(backup.get("info", {}).get("size", "")),
                status=status
            ))
        return backups

    def restore_backup_by_time(self, timestamp: int) -> str:
        log.info("Restoring backup by time")
        dt = datetime.fromtimestamp(timestamp,timezone(timedelta(hours=0)))
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        try:
            log.info("Restoring backup by time (timestamp: {}, formatted: {})".format(timestamp, formatted_time))
            return self._run_command(["./restore_time.sh", formatted_time], cwd=self.scripts_directory)
        except Exception as e:
            log.error("Point in time recovery failed")
            log.exception(e)
            self._start_database()
            raise e

    def _start_database(self):
        log.info("Starting database")
        result = self._run_command(["./start.sh"], cwd=self.scripts_directory)
        log.info("Result of starting database: ")
        log.info(result)

    def restore_backup_immediate(self, database_name: str = None) -> str:
        log.info("Restoring backup immediate")
        command = ["./restore_immediate.sh"]
        if database_name:
            command.append(database_name)
        try:
            return self._run_command(command, cwd=self.scripts_directory)
        except Exception as e:
            log.info("Immediate restore failed")
            self._start_database()
            raise e

    def get_databases(self) -> List[str]:
        log.info("Getting all databases")
        con = self._get_db_connection()
        with con.cursor() as cur:
            cur.execute(sql.SQL('SELECT datname FROM pg_database WHERE datistemplate = false;'))
            databases = [value[0] for value in cur.fetchall()]
            log.info(f"Got all databases: {databases}")
            return databases

    def get_roles(self) -> List[str]:
        log.info("Getting roles")
        con = self._get_db_connection()
        with con.cursor() as cur:
            cur.execute(sql.SQL('SELECT rolname FROM pg_roles;'))
            roles = [value[0] for value in cur.fetchall()]
            log.info(f"Got all roles: {roles}")
            return roles

    def restore_database_from_existing_stanza(self) -> str:
        log.info("Restoring database from existing stanza")
        command = ["./restore_database_from_existing_stanza.sh"]
        try:
            return self._run_command(command, cwd=self.scripts_directory)
        except Exception as e:
            log.info("Restoring database from existing stanza failed, starting database")
            self._start_database()
            raise e

    def _get_db_connection(self, dbname: Optional[str] = None) -> psycopg2.extensions.connection:
        params = self.db_params.copy()
        if dbname:
            params["dbname"] = dbname
        return psycopg2.connect(**params)

    def run_sql(self, query: str, database_name: str) -> list[tuple[Any, ...]] | str:
        log.info("Running SQL query: '{}' in database {}".format(query, database_name))
        with self._get_db_connection(database_name) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                if cur.description is not None:
                    return cur.fetchall()
                else:
                    return "Completed successfully"

    def create_database(self, dbname: str) -> None:
        con = self._get_db_connection()
        con.autocommit = True
        cur = con.cursor()
        cur.execute(sql.SQL('CREATE DATABASE {};')
        .format(
            sql.Identifier(dbname)
        ))
        con.close()

    def drop_database(self, dbname: str) -> None:
        con = self._get_db_connection()
        con.autocommit = True
        cur = con.cursor()
        cur.execute(sql.SQL('DROP DATABASE {};')
        .format(
            sql.Identifier(dbname)
        ))
        con.close()
