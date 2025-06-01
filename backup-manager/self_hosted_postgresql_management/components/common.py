import reflex as rx


def card_container(
        title: str, *children, **props
) -> rx.Component:
    additional_classes = props.pop("class_name", "")
    base_class = "bg-white p-6 rounded-lg shadow-lg border border-gray-200"
    classes_list = [base_class, additional_classes]
    combined_class = " ".join(filter(None, classes_list))
    return rx.el.div(
        rx.el.h3(
            title,
            class_name="text-xl font-semibold text-gray-800 mb-4",
        ),
        rx.el.div(*children, class_name="space-y-4"),
        class_name=combined_class,
        **props
    )


def action_button(
        text: str,
        on_click_event: (
                rx.event.EventHandler | list[rx.event.EventHandler]
        ),
        icon: str | None = None,
        loading: rx.Var[bool] | bool = False,
        **props
) -> rx.Component:
    additional_classes = props.pop("class_name", "")
    base_loading_class = "flex items-center justify-center px-4 py-2 bg-indigo-400 text-white font-medium rounded-md shadow-sm cursor-not-allowed transition-colors duration-150"
    base_not_loading_class = "flex items-center justify-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-md shadow-sm hover:shadow-md transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
    additional_classes_str = (
        additional_classes
        if isinstance(additional_classes, str)
        else ""
    )
    loading_classes_list = [
        base_loading_class,
        additional_classes_str,
    ]
    combined_loading_class = " ".join(
        filter(None, loading_classes_list)
    )
    not_loading_classes_list = [
        base_not_loading_class,
        additional_classes_str,
    ]
    combined_not_loading_class = " ".join(
        filter(None, not_loading_classes_list)
    )
    return rx.el.button(
        rx.cond(
            icon != None,
            rx.icon(icon, class_name="mr-2 h-5 w-5"),
            rx.fragment(),
        ),
        text,
        on_click=on_click_event,
        disabled=loading,
        class_name=rx.cond(
            loading,
            combined_loading_class,
            combined_not_loading_class,
        ),
        **props
    )
