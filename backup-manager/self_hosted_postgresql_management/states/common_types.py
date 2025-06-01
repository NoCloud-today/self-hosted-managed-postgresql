from typing import TypedDict, Literal


class LaunchEntry(TypedDict):
    timestamp_start: str
    timestamp_end: str
    operation_type: str
    target: str
    status: Literal["Success", "Failure", "In Progress"]
    message: str