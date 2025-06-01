import reflex as rx

NAV_ITEMS = {
    "Overview": "/",
    "Backups": "/backups",
    "Restore": "/restore",
    "Cron Schedules": "/cron",
    "Query Runner": "/query",
}


def nav_link(text: str, url: str) -> rx.Component:
    return rx.link(
        rx.el.text(
            text,
            class_name="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors",
        ),
        href=url,
    )


def navbar() -> rx.Component:
    return rx.el.nav(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "Self-hosted PostgreSQL Management",
                        class_name="text-white text-lg font-semibold ml-2",
                    ),
                    class_name="flex items-center flex-shrink-0",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.foreach(
                            list(NAV_ITEMS.items()),
                            lambda item: nav_link(
                                item[0], item[1]
                            ),
                        ),
                        class_name="flex space-x-4",
                    ),
                    class_name="hidden md:block",
                ),
                class_name="flex items-center justify-between h-16",
            ),
            class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
        ),
        class_name="bg-gray-800 shadow-md sticky top-0 z-50",
    )