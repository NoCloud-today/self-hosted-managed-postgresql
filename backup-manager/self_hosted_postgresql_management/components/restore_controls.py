import reflex as rx


def legacy_restore_controls() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            "Restore controls have moved to the Restore page.",
            class_name="text-red-500",
        )
    )
