import reflex as rx

from self_hosted_postgresql_management.components.common import card_container
from self_hosted_postgresql_management.states.general_state import GeneralState


def databases_list() -> rx.Component:
    return card_container(
        "Available Databases",
        rx.cond(
            GeneralState.is_loading_general,
            rx.el.p(
                "Loading databases...",
                class_name="text-gray-500",
            ),
            rx.el.div(
                rx.el.ul(
                    rx.foreach(
                        GeneralState.available_databases,
                        lambda db_name: rx.el.li(
                            db_name,
                            class_name="p-2 border-b border-gray-100 text-gray-700",
                        ),
                    ),
                    rx.cond(
                        ~GeneralState.is_loading_general
                        & (
                                GeneralState.available_databases.length()
                                == 0
                        ),
                        rx.el.li(
                            "No databases found.",
                            class_name="text-gray-500 p-2",
                        ),
                        rx.fragment(),
                    ),
                    class_name="list-disc list-inside space-y-1",
                ),
                rx.el.div(
                    rx.el.h3(
                        "Create New Database",
                        class_name="text-lg font-semibold text-gray-700 mt-4 mb-2",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.input(
                                placeholder="Enter database name",
                                value=GeneralState.new_database_name,
                                on_change=GeneralState.set_new_database_name,
                                class_name="w-full p-2 border border-gray-300 rounded-md",
                            ),
                            rx.el.button(
                                "Create Database",
                                type_="submit",
                                class_name="mt-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600",
                                is_disabled=GeneralState.is_loading_general,
                            ),
                            class_name="space-y-2",
                        ),
                        on_submit=GeneralState.create_database,
                        class_name="mt-2",
                    ),
                    rx.el.h3(
                        "Drop Database",
                        class_name="text-lg font-semibold text-gray-700 mt-6 mb-2",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.select(
                                rx.foreach(
                                    GeneralState.available_databases,
                                    lambda db: rx.el.option(db, value=db),
                                ),
                                value=GeneralState.database_to_drop,
                                on_change=GeneralState.set_database_to_drop,
                                placeholder="Select database to drop",
                                class_name="w-full p-2 border border-gray-300 rounded-md",
                            ),
                            rx.el.button(
                                "Drop Database",
                                type_="submit",
                                class_name="mt-2 px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600",
                                is_disabled=GeneralState.is_loading_general,
                            ),
                            class_name="space-y-2",
                        ),
                        on_submit=GeneralState.drop_database,
                        class_name="mt-2",
                    ),
                    class_name="mt-4",
                ),
            ),
        ),
    )


def users_list() -> rx.Component:
    return card_container(
        "Available roles",
        rx.cond(
            GeneralState.is_loading_general,
            rx.el.p(
                "Loading users...",
                class_name="text-gray-500",
            ),
            rx.el.ul(
                rx.foreach(
                    GeneralState.available_roles,
                    lambda user_name: rx.el.li(
                        user_name,
                        class_name="p-2 border-b border-gray-100 text-gray-700",
                    ),
                ),
                rx.cond(
                    ~GeneralState.is_loading_general
                    & (
                            GeneralState.available_roles.length()
                            == 0
                    ),
                    rx.el.li(
                        "No users found.",
                        class_name="text-gray-500 p-2",
                    ),
                    rx.fragment(),
                ),
                class_name="list-disc list-inside space-y-1",
            ),
        ),
    )


def index_page() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "System Overview",
            class_name="text-2xl font-bold text-gray-800 mb-6",
        ),
        rx.el.div(
            databases_list(),
            users_list(),
            class_name="grid md:grid-cols-2 gap-6",
        ),
        class_name="p-4 md:p-8",
        on_mount=GeneralState.load_initial_data,
    )
