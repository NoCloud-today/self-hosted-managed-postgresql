import reflex as rx

from self_hosted_postgresql_management.components.common import (
    card_container,
    action_button,
)
from self_hosted_postgresql_management.components.restore_launch_history import (
    restore_launch_history_table,
)
from self_hosted_postgresql_management.states.restore_state import RestoreState


def restore_options_component() -> rx.Component:
    return card_container(
        "Recovery Operations",
        rx.el.div(
            rx.el.h4(
                "Point-in-Time Restore",
                class_name="text-md font-semibold text-gray-700 mb-2",
            ),
            rx.el.div(
                rx.el.label(
                    "Date (YYYY-MM-DD):",
                    html_for="restore_date",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.input(
                    id="restore_date",
                    type="date",
                    default_value=RestoreState.restore_date,
                    on_change=RestoreState.set_restore_date,
                    class_name="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                ),
                class_name="mb-3",
            ),
            rx.el.div(
                rx.el.label(
                    "Time (HH:MM):",
                    html_for="restore_time",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.input(
                    id="restore_time",
                    type="time",
                    default_value=RestoreState.restore_time,
                    on_change=RestoreState.set_restore_time,
                    class_name="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                ),
                class_name="mb-3",
            ),
            action_button(
                "Start Point-in-Time Restore",
                on_click_event=lambda: RestoreState.restore_database(
                    "time"
                ),
                icon="clock",
                loading=RestoreState.is_loading,
                class_name="w-full",
            ),
            class_name="mb-6 p-4 border border-gray-200 rounded-md",
        ),
        rx.el.div(
            rx.el.h4(
                "Other Restore Options",
                class_name="text-md font-semibold text-gray-700 mb-2",
            ),
            action_button(
                "Immediate Restore",
                on_click_event=lambda: RestoreState.restore_database(
                    "immediate"
                ),
                icon="zap",
                loading=RestoreState.is_loading,
                class_name="w-full mb-3",
            ),
            action_button(
                "Existing Stanza Restore",
                on_click_event=lambda: RestoreState.restore_database(
                    "stanza"
                ),
                icon="database_zap",
                loading=RestoreState.is_loading,
                class_name="w-full",
            ),
            class_name="p-4 border border-gray-200 rounded-md",
        ),
    )


def restore_page() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Database Restore",
            class_name="text-2xl font-bold text-gray-800 mb-6",
        ),
        restore_options_component(),
        rx.el.div(
            restore_launch_history_table(),
            class_name="mt-8",
        ),
        class_name="p-4 md:p-8",
    )
