import reflex as rx
import os

config = rx.Config(
    app_name="self_hosted_postgresql_management",
    db_url=os.environ.get("DATABASE_URL", "sqlite:///data/self_hosted_postgresql_management.db"),
    env=rx.Env.DEV
)