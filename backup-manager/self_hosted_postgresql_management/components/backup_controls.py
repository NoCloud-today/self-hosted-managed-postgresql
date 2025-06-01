import reflex as rx
from self_hosted_postgresql_management.states.backup_state import BackupState
from self_hosted_postgresql_management.components.common import (
    card_container,
    action_button,
)


def backup_controls() -> rx.Component:
    return card_container(
        "Create Backups",
        action_button(
            "Incremental Backup",
            on_click_event=lambda: BackupState.create_backup(
                "incr"
            ),
            icon="plus_circle",
            loading=BackupState.is_loading,
            class_name="w-full",
        ),
        action_button(
            "Differential Backup",
            on_click_event=lambda: BackupState.create_backup(
                "diff"
            ),
            icon="copy",
            loading=BackupState.is_loading,
            class_name="w-full",
        ),
        action_button(
            "Full Backup",
            on_click_event=lambda: BackupState.create_backup(
                "full"
            ),
            icon="archive",
            loading=BackupState.is_loading,
            class_name="w-full",
        ),
    )