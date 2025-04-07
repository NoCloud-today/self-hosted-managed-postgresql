from dataclasses import dataclass

@dataclass
class Backup:
    label: str
    timestamp_start: int
    timestamp_end: int
    type: str
    size: str

@dataclass
class SQLRequest:
    query: str
    database_name: str = "postgres"