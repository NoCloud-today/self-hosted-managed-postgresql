import reflex as rx

from self_hosted_postgresql_management.states.backup_state import BackupState


def status_badge(status: str) -> rx.Component:
    return rx.el.span(
        status,
        class_name=rx.match(
            status,
            (
                "Success",
                "px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800",
            ),
            (
                "Failure",
                "px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800",
            ),
            (
                "In Progress",
                "px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800 animate-pulse",
            ),
            "px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800",
        ),
    )


def backup_launch_history_table() -> rx.Component:
    header_class = "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
    cell_class = (
        "px-6 py-4 whitespace-nowrap text-sm text-gray-700"
    )
    return rx.el.div(
        rx.el.h3(
            "Backup Launch History",
            class_name="text-2xl font-semibold text-gray-800 mb-4",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Start Time",
                            class_name=header_class,
                        ),
                        rx.el.th(
                            "End Time",
                            class_name=header_class,
                        ),
                        rx.el.th(
                            "Operation",
                            class_name=header_class,
                        ),
                        rx.el.th(
                            "Status",
                            class_name=header_class,
                        ),
                        class_name="bg-gray-50",
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        BackupState.launch_history,
                        lambda entry: rx.el.tr(
                            rx.el.td(
                                entry.timestamp_start,
                                class_name=cell_class,
                            ),
                            rx.el.td(
                                entry.timestamp_end,
                                class_name=cell_class,
                            ),
                            rx.el.td(
                                entry.operation_type,
                                class_name=cell_class,
                            ),
                            rx.el.td(
                                status_badge(
                                    entry.status
                                ),
                                class_name="px-6 py-4 whitespace-nowrap text-sm",
                            ),
                            class_name="hover:bg-gray-50 transition-colors duration-150",
                        ),
                    ),
                    rx.cond(
                        BackupState.launch_history.length()
                        == 0,
                        rx.el.tr(
                            rx.el.td(
                                "No backup launch history yet.",
                                col_span=6,
                                class_name="px-6 py-4 text-center text-sm text-gray-500",
                            )
                        ),
                        rx.fragment(),
                    ),
                    class_name="bg-white divide-y divide-gray-200",
                ),
                class_name="min-w-full divide-y divide-gray-200",
            ),
            class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
        ),
        on_mount=BackupState.update_backup_history,
    )
