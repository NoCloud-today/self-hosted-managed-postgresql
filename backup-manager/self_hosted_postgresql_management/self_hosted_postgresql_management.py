import reflex as rx

from self_hosted_postgresql_management.api.routes import fastapi_app
from self_hosted_postgresql_management.components.navbar import navbar
from self_hosted_postgresql_management.pages.backups_page import backups_page
from self_hosted_postgresql_management.pages.cron_page import cron_page
from self_hosted_postgresql_management.pages.index_page import index_page
from self_hosted_postgresql_management.pages.query_page import query_page
from self_hosted_postgresql_management.pages.restore_page import restore_page
from loguru import logger as log

def main_layout(page_content: rx.Component) -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            page_content,
            class_name="container mx-auto px-4 py-6 flex-grow",
        ),
        rx.el.footer(
            rx.el.p(
                "© 2024 PostgreSQL Management Service. Built with Reflex.",
                class_name="text-center text-sm text-gray-500 py-4 border-t border-gray-200",
            ),
            class_name="bg-gray-100 w-full",
        ),
        class_name="bg-gray-100 min-h-screen font-sans flex flex-col",
    )

@rx.page(route="/")
def index() -> rx.Component:
    return main_layout(index_page())

@rx.page(route="/backups")
def backups() -> rx.Component:
    return main_layout(backups_page())

@rx.page(route="/restore")
def restore() -> rx.Component:
    return main_layout(restore_page())

@rx.page(route="/query")
def query() -> rx.Component:
    return main_layout(query_page())

@rx.page(route="/cron")
def cron() -> rx.Component:
    return main_layout(cron_page())


app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="indigo",
        radius="medium",
    ),
    api_transformer=fastapi_app,
    stylesheets=[
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
    ],

)
log.info("Enabling state")
app._enable_state()