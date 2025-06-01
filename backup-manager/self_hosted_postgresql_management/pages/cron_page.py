import reflex as rx
from self_hosted_postgresql_management.states.cron_state import CronState
from self_hosted_postgresql_management.components.common import (
    card_container,
    action_button,
)


def next_backup_info() -> rx.Component:
    return rx.cond(
        CronState.formatted_next_scheduled_backup,
        card_container(
            "Next Scheduled Backup",
            rx.el.div(
                rx.el.p(
                    rx.el.strong("Name: "),
                    CronState.formatted_next_scheduled_backup[
                        "description"
                    ],
                    class_name="text-gray-700",
                ),
                rx.el.p(
                    rx.el.strong("Backup Type: "),
                    CronState.formatted_next_scheduled_backup[
                        "backup_type"
                    ],
                    class_name="text-gray-700",
                ),
                rx.el.p(
                    rx.el.strong("Schedule: "),
                    CronState.formatted_next_scheduled_backup[
                        "schedule_expression"
                    ],
                    class_name="text-gray-700",
                ),
                rx.el.p(
                    rx.el.strong("Next Run: "),
                    CronState.formatted_next_scheduled_backup[
                        "next_run_time"
                    ],
                    class_name="text-green-600 font-semibold",
                ),
                class_name="space-y-2",
            ),
            class_name="mb-6 bg-indigo-50 border-indigo-200",
        ),
        rx.cond(
            CronState.is_loading,
            rx.el.p(
                "Loading next backup info...",
                class_name="text-gray-500",
            ),
            rx.el.p(
                "No scheduled backups found or data is loading.",
                class_name="text-gray-500",
            ),
        ),
    )


def cron_schedules_table() -> rx.Component:
    header_classes = "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
    cell_classes = (
        "px-6 py-4 whitespace-nowrap text-sm text-gray-700"
    )
    return rx.el.div(
        rx.el.h3(
            "All Scheduled Backups",
            class_name="text-xl font-semibold text-gray-800 mb-4",
        ),
        action_button(
            "Refresh Schedules",
            on_click_event=CronState.load_cron_jobs,
            icon="refresh_cw",
            loading=CronState.is_loading,
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Schedule",
                            class_name=header_classes,
                        ),
                        rx.el.th(
                            "Backup Type",
                            class_name=header_classes,
                        ),
                        rx.el.th(
                            "Name",
                            class_name=header_classes,
                        ),
                        rx.el.th(
                            "Next Run Time",
                            class_name=header_classes,
                        ),
                        rx.el.th(
                            "Actions",
                            class_name=header_classes,
                        ),
                        class_name="bg-gray-50",
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        CronState.formatted_cron_jobs,
                        lambda job: rx.el.tr(
                            rx.el.td(
                                job["schedule_expression"],
                                class_name=cell_classes,
                            ),
                            rx.el.td(
                                job["backup_type"],
                                class_name=cell_classes,
                            ),
                            rx.el.td(
                                job["name"],
                                class_name=f"{cell_classes} max-w-xs truncate",
                            ),
                            rx.el.td(
                                job["next_run_time"],
                                class_name=cell_classes,
                            ),
                            rx.el.td(
                                rx.button(
                                    "Delete",
                                    on_click=lambda: CronState.delete_backup_schedule(job["id"]),
                                    class_name="text-white-600 hover:text-white-900 font-medium",
                                ),
                                class_name=cell_classes,
                            ),
                            class_name="hover:bg-gray-50 transition-colors duration-150",
                        ),
                    ),
                    rx.cond(
                        CronState.is_loading,
                        rx.el.tr(
                            rx.el.td(
                                "Loading schedules...",
                                col_span=5,
                                class_name="px-6 py-4 text-center text-sm text-gray-500",
                            )
                        ),
                        rx.cond(
                            ~CronState.is_loading
                            & (
                                CronState.formatted_cron_jobs.length()
                                == 0
                            ),
                            rx.el.tr(
                                rx.el.td(
                                    "No cron schedules configured.",
                                    col_span=5,
                                    class_name="px-6 py-4 text-center text-sm text-gray-500",
                                )
                            ),
                            rx.fragment(),
                        ),
                    ),
                    class_name="bg-white divide-y divide-gray-200",
                ),
                class_name="min-w-full divide-y divide-gray-200",
            ),
            class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
        ),
    )


def create_backup_form() -> rx.Component:
    return card_container(
        "Create New Backup Schedule",
        rx.form(
            rx.el.div(
                rx.el.label(
                    "Backup Type",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.select(
                    ["full", "incr", "diff"],
                    placeholder="Select backup type",
                    id="job_type",
                    on_change=CronState.set_job_type,
                    value=CronState.selected_job_type,
                    class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Schedule Time",
                    class_name="block text-sm font-medium text-gray-700 mb-1",
                ),
                rx.el.div(
                    rx.input(
                        type="time",
                        id="schedule_time",
                        on_change=CronState.set_schedule_time,
                        value=CronState.selected_schedule_time,
                        class_name="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm",
                    ),
                    class_name="relative",
                ),
                class_name="mb-4",
            ),
            rx.button(
                "Create Schedule",
                type_="submit",
                class_name="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500",
            ),
            on_submit=CronState.create_backup_schedule,
        ),
        class_name="mb-6",
    )


def cron_page() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Cron Backup Schedules",
            class_name="text-2xl font-bold text-gray-800 mb-6",
        ),
        create_backup_form(),
        next_backup_info(),
        cron_schedules_table(),
        class_name="p-4 md:p-8",
        on_mount=CronState.load_cron_jobs,
    )