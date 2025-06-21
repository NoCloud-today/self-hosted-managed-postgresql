import asyncio
import datetime
from typing import Literal, cast, Any

import reflex as rx
from self_hosted_postgresql_management.services.backup_service import BackupService
from self_hosted_postgresql_management.states.common_types import LaunchEntry
from self_hosted_postgresql_management.db.database_models import QueryHistory
from loguru import logger as log
_backup_service: BackupService = BackupService()


class GeneralState(rx.State):
    sql_launch_history: list[LaunchEntry] = []
    is_loading_general: bool = False
    is_loading_sql: bool = False
    sql_query_input: str = ""
    sql_query_result: list[tuple[Any, ...]] = []
    available_databases: list[str] = []
    selected_database: str = ""
    available_roles: list[str] = []
    new_database_name: str = ""
    database_to_drop: str = ""

    @rx.event(background=True)
    async def load_initial_data(self):
        yield GeneralState.load_sql_history
        async with self:
            self.is_loading_general = True
            yield
        while True:
            try:
                databases = await asyncio.to_thread(
                    _backup_service.get_databases
                )
                roles = await asyncio.to_thread(
                    _backup_service.get_roles
                )
                async with self:
                    self.available_databases = databases
                    if databases and (
                            not self.selected_database
                    ):
                        self.selected_database = databases[0]
                    self.available_roles = roles
                    yield
            except Exception as e:
                await asyncio.sleep(100)
            finally:
                async with self:
                    self.is_loading_general = False
                    yield
            await asyncio.sleep(100)

    @rx.event(background=True)
    async def load_sql_history(self):
        with rx.session() as session:
            history = session.exec(
                QueryHistory.select().order_by(QueryHistory.timestamp_start)
            ).all()
            async with self:
                self.sql_launch_history = [
                    cast(LaunchEntry, {
                        "timestamp_start": h.timestamp_start.strftime("%Y-%m-%d %H:%M:%S"),
                        "timestamp_end": h.timestamp_end.strftime("%Y-%m-%d %H:%M:%S") if h.timestamp_end else "",
                        "operation_type": h.operation_type,
                        "target": h.target,
                        "status": h.status,
                        "message": h.message,
                    }) for h in history
                ]

    def _add_sql_launch_entry(
            self,
            operation_type: str,
            target: str,
            status: Literal[
                "Success", "Failure", "In Progress"
            ],
            message: str,
            start_time: datetime.datetime,
    ):
        entry_dict = {
            "timestamp_start": start_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "timestamp_end": "",
            "operation_type": operation_type,
            "target": target,
            "status": status,
            "message": message,
        }
        self.sql_launch_history.insert(
            0, cast(LaunchEntry, entry_dict)
        )
        
        # Save to database
        with rx.session() as session:
            history_entry = QueryHistory(
                timestamp_start=start_time,
                operation_type=operation_type,
                target=target,
                status=status,
                message=message,
                database_name=self.selected_database,
                sql_query=self.sql_query_input
            )
            session.add(history_entry)
            session.commit()

    def _update_sql_launch_entry(
            self,
            operation_type: str,
            target: str,
            status: Literal["Success", "Failure"],
            message: str,
            start_time: datetime.datetime,
            end_time: datetime.datetime
    ):
        # Update in-memory history
        for entry in self.sql_launch_history:
            if (
                entry["operation_type"] == operation_type
                and entry["target"] == target
                and entry["timestamp_start"] == start_time.strftime("%Y-%m-%d %H:%M:%S")
                and entry["status"] == "In Progress"
            ):
                entry["status"] = status
                entry["message"] = message
                entry["timestamp_end"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
                break

        # Update database entry
        with rx.session() as session:
            history_entry = session.exec(
                QueryHistory.select().where(
                    QueryHistory.timestamp_start == start_time,
                    QueryHistory.operation_type == operation_type,
                    QueryHistory.target == target,
                    QueryHistory.status == "In Progress"
                )
            ).first()
            if history_entry:
                history_entry.status = status
                history_entry.message = message
                history_entry.timestamp_end = end_time
                session.commit()

    @rx.event
    def set_sql_query_input(self, value: str):
        self.sql_query_input = value

    @rx.event
    def set_selected_database(self, db_name: str):
        self.selected_database = db_name
        yield rx.toast.info(
            f"Database context changed to: {db_name}"
        )

    @rx.event(background=True)
    async def execute_sql_query(self):
        if not self.sql_query_input.strip():
            yield rx.toast.error(
                "SQL query cannot be empty."
            )
            return
        if not self.selected_database:
            yield rx.toast.error(
                "Please select a database first."
            )
            return
        start_time = datetime.datetime.now()
        async with self:
            self.is_loading_sql = True
            target_info = f"DB: {self.selected_database} - Query: {self.sql_query_input[:20]}..."
            self._add_sql_launch_entry(
                "SQL Query Execution",
                target_info,
                "In Progress",
                f"Executing SQL on '{self.selected_database}': {self.sql_query_input[:50]}...",
                start_time,
            )
            yield
        current_status = "Success"
        response = ""
        try:
            response = await asyncio.to_thread(
                lambda: _backup_service.run_sql(self.sql_query_input, self.selected_database)
            )
        except Exception as e:
            current_status = "Failure"
            response = str(e)
        end_time = datetime.datetime.now()
        async with self:
            self.sql_query_result = [(response,)] if isinstance(response,str) else response
            self._update_sql_launch_entry(
                "SQL Query Execution",
                target_info,
                current_status,
                f"SQL Query ({target_info}) {current_status}: {response}",
                start_time,
                end_time
            )
            if current_status == "Success":
                yield rx.toast.success(
                    f"SQL query on '{self.selected_database}' successful: {response}"
                )
            else:
                yield rx.toast.error(
                    f"SQL query on '{self.selected_database}' failed: {response}"
                )
        async with self:
            self.is_loading_sql = False
            yield

    @rx.var
    def formatted_sql_launch_history(
            self,
    ) -> list[dict[str, str]]:
        return [
            {
                "timestamp": entry["timestamp_start"],
                "operation_type": entry["operation_type"],
                "target": entry["target"],
                "status": entry["status"],
                "message": entry["message"],
            }
            for entry in self.sql_launch_history
        ]

    @rx.event(background=True)
    async def create_database(self):
        if not self.new_database_name.strip():
            yield rx.toast.error("Database name cannot be empty.")
            return

        start_time = datetime.datetime.now()
        async with self:
            self.is_loading_general = True
            self._add_sql_launch_entry(
                "Create Database",
                self.new_database_name,
                "In Progress",
                f"Creating database '{self.new_database_name}'...",
                start_time,
            )
            yield

        current_status = "Success"
        try:
            await asyncio.to_thread(
                lambda: _backup_service.create_database(self.new_database_name)
            )
            log.info(f"Database {self.database_to_drop }dropped")
            databases = await asyncio.to_thread(_backup_service.get_databases)
            log.info(f"Refreshed database list")
            async with self:
                self.available_databases = databases
                self.new_database_name = ""
                yield

            log.info(f"Refreshed database state on frontend")
        except Exception as e:
            current_status = "Failure"
            async with self:
                yield rx.toast.error(f"Failed to create database: {str(e)}")
        finally:
            end_time = datetime.datetime.now()
            log.info("Starting to run end section")
            async with self:
                self.is_loading_general = False
                for entry in self.sql_launch_history:
                    if (
                            entry["operation_type"] == "Create Database"
                            and entry["target"] == self.new_database_name
                            and entry["status"] == "In Progress"
                    ):
                        entry["status"] = current_status
                        entry["message"] = f"Database creation {current_status.lower()}"
                        entry["timestamp_end"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
                        break
                yield

    @rx.event(background=True)
    async def drop_database(self):
        if not self.database_to_drop:
            yield rx.toast.error("Please select a database to drop.")
            return

        start_time = datetime.datetime.now()
        async with self:
            self.is_loading_general = True
            self._add_sql_launch_entry(
                "Drop Database",
                self.database_to_drop,
                "In Progress",
                f"Dropping database '{self.database_to_drop}'...",
                start_time,
            )
            yield

        current_status = "Success"
        try:
            await asyncio.to_thread(
                lambda: _backup_service.drop_database(self.database_to_drop)
            )
            log.info(f"Database {self.database_to_drop }dropped")
            databases = await asyncio.to_thread(_backup_service.get_databases)
            log.info(f"Refreshed database list")

            async with self:
                self.available_databases = databases
                self.database_to_drop = ""
                if self.selected_database == self.database_to_drop:
                    self.selected_database = databases[0] if databases else ""
                yield rx.toast.success(f"Database {self.selected_database} dropped")
            log.info(f"Refreshed database state on frontend")
        except Exception as e:
            current_status = "Failure"
            yield rx.toast.error(f"Failed to drop database: {str(e)}")
        finally:
            end_time = datetime.datetime.now()
            async with self:
                self.is_loading_general = False
                for entry in self.sql_launch_history:
                    if (
                            entry["operation_type"] == "Drop Database"
                            and entry["target"] == self.database_to_drop
                            and entry["status"] == "In Progress"
                    ):
                        entry["status"] = current_status
                        entry["message"] = f"Database deletion {current_status.lower()}"
                        entry["timestamp_end"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
                        break
                yield
