import time
from typing import List


def test_full_backup_pipeline(backup_client, db_utils, test_database, test_table):
    """Test pipeline: Create data -> Full backup -> Add data -> Restore -> Verify"""
    initial_data = ["'initial_data_1'", "'initial_data_2'"]
    db_utils.insert_data(test_database, test_table, initial_data)
    
    result = backup_client.create_full_backup()
    assert "message" in result
    assert "details" in result
    
    additional_data = ["'additional_data_1'", "'additional_data_2'"]
    db_utils.insert_data(test_database, test_table, additional_data)
    
    result = db_utils.execute_query(test_database, f"SELECT data FROM {test_table}")
    assert len(result) == 4
    
    result = backup_client.restore_backup_immediate(test_database)
    assert "message" in result
    assert "details" in result
    
    result = db_utils.execute_query(test_database, f"SELECT data FROM {test_table}")
    assert len(result) == 2


def test_incremental_backup_pipeline(backup_client, db_utils, test_database, test_table):
    """Test pipeline: Full backup -> Add data -> Incremental backup -> Add data -> Restore -> Verify"""
    initial_data = ["'initial_data_1'", "'initial_data_2'"]
    db_utils.insert_data(test_database, test_table, initial_data)
    backup_client.create_full_backup()
    
    additional_data = ["'additional_data_1'", "'additional_data_2'"]
    db_utils.insert_data(test_database, test_table, additional_data)
    backup_client.create_incremental_backup()
    
    final_data = ["'final_data_1'", "'final_data_2'"]
    db_utils.insert_data(test_database, test_table, final_data)
    result = db_utils.execute_query(test_database, f"SELECT data FROM {test_table}")
    assert len(result) == 6
    result = backup_client.restore_backup_immediate(test_database)
    assert "message" in result
    assert "details" in result
    
    result = db_utils.execute_query(test_database, f"SELECT data FROM {test_table}")
    assert len(result) == 4


def test_differential_backup_pipeline(backup_client, db_utils, test_database, test_table):
    """Test pipeline: Full backup -> Add data -> Differential backup -> Add data -> Restore -> Verify"""
    initial_data = ["'initial_data_1'", "'initial_data_2'"]
    db_utils.insert_data(test_database, test_table, initial_data)
    backup_client.create_full_backup()
    
    additional_data = ["'additional_data_1'", "'additional_data_2'"]
    db_utils.insert_data(test_database, test_table, additional_data)
    backup_client.create_diff_backup()
    
    final_data = ["'final_data_1'", "'final_data_2'"]
    db_utils.insert_data(test_database, test_table, final_data)
    
    result = db_utils.execute_query(test_database, f"SELECT data FROM {test_table}")
    assert len(result) == 6
    
    result = backup_client.restore_backup_immediate(test_database)
    assert "message" in result
    assert "details" in result
    
    result = db_utils.execute_query(test_database, f"SELECT data FROM {test_table}")
    assert len(result) == 4


def test_point_in_time_restore_pipeline(backup_client, db_utils, test_database, test_table):
    """Test pipeline: Create data -> Full backup -> Add data -> Capture time -> Add data -> Restore to time -> Verify"""
    initial_data = ["'initial_data_1'", "'initial_data_2'"]
    db_utils.insert_data(test_database, test_table, initial_data)
    backup_client.create_full_backup()
    
    additional_data = ["'additional_data_1'", "'additional_data_2'"]
    db_utils.insert_data(test_database, test_table, additional_data)
    
    time.sleep(2)
    timestamp = int(time.time())
    time.sleep(2)
    
    final_data = ["'final_data_1'", "'final_data_2'"]
    db_utils.insert_data(test_database, test_table, final_data)
    
    result = db_utils.execute_query(test_database, f"SELECT data FROM {test_table}")
    assert len(result) == 6
    
    result = backup_client.restore_backup_by_time(timestamp)
    assert "message" in result
    assert "details" in result
    
    result = db_utils.execute_query(test_database, f"SELECT data FROM {test_table}")
    assert len(result) == 4


def test_backup_listing_pipeline(backup_client, db_utils, test_database, test_table):
    """Test pipeline: Create multiple backups -> List backups -> Verify"""
    initial_data = ["'initial_data_1'", "'initial_data_2'"]
    db_utils.insert_data(test_database, test_table, initial_data)
    backup_client.create_full_backup()
    
    additional_data = ["'additional_data_1'", "'additional_data_2'"]
    db_utils.insert_data(test_database, test_table, additional_data)
    backup_client.create_incremental_backup()

    final_data = ["'final_data_1'", "'final_data_2'"]
    db_utils.insert_data(test_database, test_table, final_data)
    backup_client.create_diff_backup()

    backups = backup_client.list_backups()
    assert len(backups) >= 3

    backup_types = {backup["type"] for backup in backups}
    assert "full" in backup_types
    assert "incr" in backup_types
    assert "diff" in backup_types
