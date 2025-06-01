import reflex as rx

from self_hosted_postgresql_management.components.common import (
    action_button,
    card_container,
)
from self_hosted_postgresql_management.components.general_launch_history import (
    general_launch_history_table,
)
from self_hosted_postgresql_management.states.general_state import GeneralState


def database_selection_component() -> rx.Component:
    return card_container(
        "Database Context",
        rx.el.div(
            rx.el.label(
                "Select Database:",
                html_for="db_select",
                class_name="block text-sm font-medium text-gray-700 mb-1",
            ),
            rx.el.select(
                rx.foreach(
                    GeneralState.available_databases,
                    lambda db: rx.el.option(db, value=db),
                ),
                id="db_select",
                value=GeneralState.selected_database,
                on_change=GeneralState.set_selected_database,
                class_name="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                is_disabled=GeneralState.is_loading_general,
            ),
            class_name="mb-4",
        ),
        class_name="mb-6",
    )


def query_runner_component() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "SQL Query Runner",
            class_name="text-xl font-semibold text-gray-800 mb-4",
        ),
        rx.el.p(
            "Current Database: ",
            rx.el.strong(
                GeneralState.selected_database,
                class_name="text-indigo-600",
            ),
            class_name="mb-3 text-sm text-gray-600",
        ),
        rx.el.div(
            rx.el.label(
                "Enter SQL Query:",
                html_for="sql_query_input",
                class_name="block text-sm font-medium text-gray-700 mb-1",
            ),
            rx.el.textarea(
                id="sql_query_input",
                default_value=GeneralState.sql_query_input,
                on_change=GeneralState.set_sql_query_input,
                placeholder="SELECT * FROM your_table;",
                class_name="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm font-mono",
                rows=5,
            ),
            class_name="mb-4",
        ),
        action_button(
            "Execute Query",
            on_click_event=GeneralState.execute_sql_query,
            icon="play",
            loading=GeneralState.is_loading_sql,
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.h4(
                "Query Result:",
                class_name="text-md font-semibold text-gray-700 mb-2",
            ),
            rx.el.div(
                rx.cond(
                    GeneralState.sql_query_result == "",
                    rx.el.p(
                        "No query executed yet or no results.",
                        class_name="text-gray-500",
                    ),
                    rx.cond(
                        GeneralState.sql_query_result.length() == 0,
                        rx.el.p(
                            "Query returned an empty result set.",
                            class_name="text-gray-500",
                        ),
                        rx.el.div(
                            rx.el.table(
                                rx.el.tbody(
                                    rx.foreach(
                                        GeneralState.sql_query_result,
                                        lambda row: rx.el.tr(
                                            rx.foreach(
                                                row,
                                                lambda cell: rx.el.td(
                                                    cell,  # Directly render cell value
                                                    class_name="px-4 py-2 whitespace-nowrap text-sm text-gray-500 border-b",
                                                )
                                            )
                                        )
                                    )
                                ),
                                class_name="min-w-full divide-y divide-gray-200 border rounded-md",
                            ),
                            class_name="overflow-x-auto border rounded-md",
                        )
                    ),
                ),
                class_name="min-h-[50px]",
            ),
        ),
        class_name="bg-gray-50 p-6 rounded-lg shadow",
    )


def query_page() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Database Query Tool",
            class_name="text-2xl font-bold text-gray-800 mb-6",
        ),
        database_selection_component(),
        query_runner_component(),
        rx.el.div(
            general_launch_history_table(),
            class_name="mt-8",
        ),
        class_name="p-4 md:p-8",
        on_mount=GeneralState.load_initial_data,
    )
