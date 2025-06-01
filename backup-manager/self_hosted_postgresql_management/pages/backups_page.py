import reflex as rx
from self_hosted_postgresql_management.components.backup_controls import backup_controls
from self_hosted_postgresql_management.components.backup_launch_history import (
    backup_launch_history_table,
)


def backups_page() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Backup Management",
            class_name="text-2xl font-bold text-gray-800 mb-6",
        ),
        rx.el.div(backup_controls(), class_name="mb-8"),
        rx.el.div(backup_launch_history_table()),
        class_name="p-4 md:p-8",
    )