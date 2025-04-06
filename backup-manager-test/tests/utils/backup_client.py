from typing import Optional

import requests


class BackupClient:
    def __init__(self, base_url: str = "http://backup-manager:8000"):
        self.base_url = base_url

    def create_incremental_backup(self) -> dict:
        response = requests.post(f"{self.base_url}/backup/incr", timeout=60)
        response.raise_for_status()
        print("Response:", response)
        return response.json()

    def create_full_backup(self) -> dict:
        response = requests.post(f"{self.base_url}/backup/full", timeout=60)
        response.raise_for_status()
        print("Response:", response)
        return response.json()

    def create_diff_backup(self) -> dict:
        response = requests.post(f"{self.base_url}/backup/diff", timeout=60)
        response.raise_for_status()
        print("Response:", response)
        return response.json()

    def list_backups(self) -> list[dict]:
        response = requests.get(f"{self.base_url}/backups", timeout=60)
        response.raise_for_status()
        print("Response:", response)
        return response.json()

    def restore_backup_by_time(self, timestamp: int) -> dict:
        response = requests.post(f"{self.base_url}/restore/time", params={"timestamp": timestamp}, timeout=60)
        response.raise_for_status()
        print("Response:", response)
        return response.json()

    def restore_backup_immediate(self, database_name: Optional[str] = None) -> dict:
        params = {"database_name": database_name} if database_name else {}
        response = requests.post(f"{self.base_url}/restore/immediate", params=params, timeout=60)
        response.raise_for_status()
        print("Response:", response)
        return response.json()
