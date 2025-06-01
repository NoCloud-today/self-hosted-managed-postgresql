import asyncio
import datetime
from typing import Literal, cast

import reflex as rx

from self_hosted_postgresql_management.api.models import *
from self_hosted_postgresql_management.services.backup_service import BackupService
from self_hosted_postgresql_management.states.common_types import LaunchEntry

_backup_service: BackupService = BackupService()

class BackupState(rx.State):
    launch_history: list[LaunchEntry] = []
    is_loading: bool = False

    def _format_date(self, timestamp: int) -> str:
        if timestamp is None:
            return ""
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    @rx.event(background=True)
    async def create_backup(
            self, backup_type: Literal["incr", "diff", "full"]
    ):
        async with self:
            self.is_loading = True
            yield
        operation_name = (
            f"{backup_type.capitalize()} Backup"
        )
        service_message = ""
        try:
            if backup_type == "incr":
                service_message = await asyncio.to_thread(
                    _backup_service.create_incremental_backup
                )
            elif backup_type == "diff":
                service_message = await asyncio.to_thread(
                    _backup_service.create_diff_backup
                )
            elif backup_type == "full":
                service_message = await asyncio.to_thread(
                    _backup_service.create_full_backup
                )
            if (
                    "fail" in service_message.lower()
                    or "error" in service_message.lower()
            ):
                success = False
            else:
                success = True
            async with self:
                if success:
                    yield rx.toast.success(
                        f"{operation_name} initiated"
                    )
                else:
                    yield rx.toast.error(
                        f"{operation_name} failed"
                    )
        except Exception as e:
            error_message_detail = f"Unexpected error during {operation_name}: {str(e)}"
            async with self:
                yield rx.toast.error(error_message_detail)
        finally:
            async with self:
                self.is_loading = False
                yield
            yield BackupState.update_backup_history

    @rx.event(background=True)
    async def update_backup_history(self):
        backup_log_list: list[Backup] = (
            await asyncio.to_thread(
                _backup_service.list_backups
            )
        )
        processed_launch_entries: list[LaunchEntry] = []
        for backup in reversed(backup_log_list):
            launch_entry_dict = {
                "timestamp_start": self._format_date(backup.timestamp_start),
                "timestamp_end": self._format_date(backup.timestamp_end),
                "operation_type": f"{backup.type.capitalize()} Backup",
                "target": "",
                "status": backup.status,
                "message": "",
            }
            processed_launch_entries.append(
                cast(LaunchEntry, launch_entry_dict)
            )
        async with self:
            self.launch_history = processed_launch_entries
            yield


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
