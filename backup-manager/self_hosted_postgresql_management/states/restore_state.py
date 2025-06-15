import reflex as rx
from typing import Literal, Optional, cast
import datetime
import time
import asyncio
from self_hosted_postgresql_management.services.backup_service import BackupService
from self_hosted_postgresql_management.states.common_types import LaunchEntry
from self_hosted_postgresql_management.db.database_models import RestoreHistory


class RestoreState(rx.State):
    launch_history: list[LaunchEntry] = []
    is_loading: bool = False
    restore_date: str = datetime.date.today().isoformat()
    restore_time: str = datetime.datetime.now().strftime(
        "%H:%M"
    )
    _backup_service: BackupService = BackupService()

    @rx.event(background=True)
    async def load_restore_history(self):
        with rx.session() as session:
            history = session.exec(
                RestoreHistory.select().order_by(RestoreHistory.timestamp_start)
            ).all()
            self.launch_history = [
                cast(LaunchEntry, {
                    "timestamp_start": h.timestamp_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp_end": h.timestamp_end.strftime("%Y-%m-%d %H:%M:%S") if h.timestamp_end else "",
                    "operation_type": h.operation_type,
                    "target": h.target,
                    "status": h.status,
                    "message": h.message,
                }) for h in history
            ]

    def _add_launch_entry(
        self,
        operation_type: str,
        target: str,
        status: Literal[
            "Success", "Failure", "In Progress"
        ],
        message: str,
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None,
    ):
        entry_dict = {
            "timestamp_start": start_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "timestamp_end": (
                end_time.strftime("%Y-%m-%d %H:%M:%S")
                if end_time
                else ""
            ),
            "operation_type": operation_type,
            "target": target,
            "status": status,
            "message": message,
        }
        updated_existing = False
        for i, entry in enumerate(self.launch_history):
            if (
                entry["timestamp_start"]
                == entry_dict["timestamp_start"]
                and entry["operation_type"]
                == operation_type
                and (entry["status"] == "In Progress")
            ):
                self.launch_history[i] = cast(
                    LaunchEntry, entry_dict
                )
                updated_existing = True
                break
        if not updated_existing:
            self.launch_history.insert(
                0, cast(LaunchEntry, entry_dict)
            )

        with rx.session() as session:
            if updated_existing:
                history_entry = session.exec(
                    RestoreHistory.select().where(
                        RestoreHistory.timestamp_start == start_time,
                        RestoreHistory.operation_type == operation_type,
                        RestoreHistory.status == "In Progress"
                    )
                ).first()
                if history_entry:
                    history_entry.status = status
                    history_entry.message = message
                    history_entry.timestamp_end = end_time
            else:
                history_entry = RestoreHistory(
                    timestamp_start=start_time,
                    timestamp_end=end_time,
                    operation_type=operation_type,
                    target=target,
                    status=status,
                    message=message
                )
                session.add(history_entry)
            session.commit()

    @rx.event(background=True)
    async def restore_database_service_call(
        self,
        restore_type: Literal[
            "time", "immediate", "stanza"
        ],
        timestamp_arg: Optional[int] = None,
        database_name_arg: Optional[str] = None,
    ):
        start_time = datetime.datetime.now()
        operation_name_map = {
            "time": "Point-in-Time Restore",
            "immediate": "Immediate Restore",
            "stanza": "Existing Stanza Restore",
        }
        operation_name = operation_name_map[restore_type]
        target_info = restore_type.capitalize()
        if restore_type == "time" and timestamp_arg:
            target_info = f"PITR to {datetime.datetime.fromtimestamp(timestamp_arg).strftime('%Y-%m-%d %H:%M')}"
        elif (
            restore_type == "immediate"
            and database_name_arg
        ):
            target_info = (
                f"Immediate Restore for {database_name_arg}"
            )
        elif restore_type == "immediate":
            target_info = "Immediate Restore (default DB)"
        async with self:
            self.is_loading = True
            self._add_launch_entry(
                operation_name,
                target_info,
                "In Progress",
                f"Starting {operation_name} ({target_info})...",
                start_time,
            )
            yield
        try:
            if (
                restore_type == "time"
                and timestamp_arg is not None
            ):
                service_message = await asyncio.to_thread(
                    self._backup_service.restore_backup_by_time,
                    timestamp_arg,
                )
            elif restore_type == "immediate":
                service_message = await asyncio.to_thread(
                    self._backup_service.restore_backup_immediate,
                    database_name_arg,
                )
            elif restore_type == "stanza":
                service_message = await asyncio.to_thread(
                    self._backup_service.restore_database_from_existing_stanza
                )
            else:
                service_message = "Error: Invalid restore type or arguments."
            if (
                "fail" in service_message.lower()
                or "error" in service_message.lower()
            ):
                success = False
            else:
                success = True
            current_status: Literal[
                "Success", "Failure"
            ] = ("Success" if success else "Failure")
            final_message = f"{operation_name} ({target_info}) {current_status}: {service_message}"
            end_time = datetime.datetime.now()
            async with self:
                self._add_launch_entry(
                    operation_name,
                    target_info,
                    current_status,
                    final_message,
                    start_time,
                    end_time,
                )
                if success:
                    yield rx.toast.success(
                        f"{operation_name} initiated"
                    )
                else:
                    yield rx.toast.error(
                        f"{operation_name} failed"
                    )
        except Exception as e:
            end_time = datetime.datetime.now()
            error_message = f"Unexpected error during {operation_name} ({target_info}): {str(e)[:100]}"
            async with self:
                self._add_launch_entry(
                    operation_name,
                    target_info,
                    "Failure",
                    error_message,
                    start_time,
                    end_time,
                )
                yield rx.toast.error(error_message)
        finally:
            async with self:
                self.is_loading = False
                yield

    @rx.event
    def restore_database(
        self,
        restore_type: Literal[
            "time", "immediate", "stanza"
        ],
    ):
        params_timestamp: Optional[int] = None
        db_name_for_immediate: Optional[str] = None
        if restore_type == "time":
            if (
                not self.restore_date
                or not self.restore_time
            ):
                return rx.toast.error(
                    "Date and Time are required for point-in-time restore."
                )
            try:
                datetime_str = f"{self.restore_date} {self.restore_time}"
                dt_object = datetime.datetime.strptime(
                    datetime_str, "%Y-%m-%d %H:%M"
                )
                params_timestamp = int(
                    time.mktime(dt_object.timetuple())
                )
            except ValueError:
                return rx.toast.error(
                    "Invalid date or time format. Use YYYY-MM-DD and HH:MM."
                )
        return RestoreState.restore_database_service_call(
            restore_type,
            timestamp_arg=params_timestamp,
            database_name_arg=db_name_for_immediate,
        )

    @rx.event
    def set_restore_date(self, value: str):
        self.restore_date = value

    @rx.event
    def set_restore_time(self, value: str):
        self.restore_time = value

    @rx.var
    def formatted_launch_history(
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
            for entry in self.launch_history
        ]