import subprocess
from unittest.mock import patch, MagicMock

import pytest
from app.src.api.models import Backup
from app.src.services.backup_service import BackupService


@pytest.fixture
def backup_service():
    return BackupService()


@pytest.fixture
def mock_backup_info():
    return [{
        "backup": [
            {
                "label": "20240306-123456",
                "timestamp": {"start": 1709726400, "end": 1709726401},
                "type": "full",
                "info": {"size": "1.2GB"}
            }
        ]
    }]


def test_create_full_backup(backup_service):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout="Backup completed successfully", returncode=0)
        result = backup_service.create_full_backup()
        assert result == "Backup completed successfully"
        mock_run.assert_called_once_with(
            ["./backup_full.sh"],
            capture_output=True,
            text=True,
            cwd="/app/app/scripts"
        )


def test_create_incremental_backup(backup_service):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout="Incremental backup completed", returncode=0)
        result = backup_service.create_incremental_backup()
        assert result == "Incremental backup completed"
        mock_run.assert_called_once_with(
            ["./backup_incr.sh"],
            capture_output=True,
            text=True,
            cwd="/app/app/scripts"
        )


def test_create_diff_backup(backup_service):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout="Differential backup completed", returncode=0)
        result = backup_service.create_diff_backup()
        assert result == "Differential backup completed"
        mock_run.assert_called_once_with(
            ["./backup_diff.sh"],
            capture_output=True,
            text=True,
            cwd="/app/app/scripts"
        )


def test_list_backups(backup_service, mock_backup_info):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout=str(mock_backup_info).replace("\'", "\""), returncode=0)
        backups = backup_service.list_backups()
        assert len(backups) == 1
        assert isinstance(backups[0], Backup)
        assert backups[0].label == "20240306-123456"
        assert backups[0].type == "full"
        assert backups[0].size == "1.2GB"


def test_list_backups_empty(backup_service):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout="[]")
        with pytest.raises(Exception):
            backup_service.list_backups()


def test_restore_backup_by_time(backup_service):
    timestamp = 1709726400
    expected_iso_time = "2024-03-06 12:00:00"
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout="Restore completed successfully", returncode=0)
        result = backup_service.restore_backup_by_time(timestamp)
        assert result == "Restore completed successfully"
        mock_run.assert_called_once_with(
            ["./restore_time.sh", expected_iso_time],
            capture_output=True,
            text=True,
            cwd="/app/app/scripts"
        )


def test_restore_backup_immediate(backup_service):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout="Immediate restore completed", returncode=0)
        result = backup_service.restore_backup_immediate()
        assert result == "Immediate restore completed"
        mock_run.assert_called_once_with(
            ["./restore_immediate.sh"],
            capture_output=True,
            text=True,
            cwd="/app/app/scripts"
        )


def test_restore_backup_immediate_with_database(backup_service):
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(stdout="Immediate restore completed", returncode=0)
        result = backup_service.restore_backup_immediate("testdb")
        assert result == "Immediate restore completed"
        mock_run.assert_called_once_with(
            ["./restore_immediate.sh", "testdb"],
            capture_output=True,
            text=True,
            cwd="/app/app/scripts"
        )


def test_run_command_error(backup_service):
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "test", stderr="Error occurred")
        with pytest.raises(Exception):
            backup_service._run_command(["test"])
