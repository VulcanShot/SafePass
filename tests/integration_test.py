import safepass.safepass as safepass
import test_utils
import pytest
import logging

def test_workflow(monkeypatch, caplog):
    inputs = [
        test_utils.TEST_PASSWORD, test_utils.TEST_PASSWORD,
        'n', 'Moodle', 'moodle.warwick.ac.uk', 'TestUser', 'MyPaSsWoRd99!', ' ',
        'n', 'moodle', 'Burner', 'xXsecretXx-', ' ', # 'moodle' should be compared as case-insensitive
        'd', ' ',
        'r', 'Moodle', '1', ' '
        'g', 'moodle', ' ',
        '6'
    ]
    
    test_utils.new_mock_db(monkeypatch)
    test_utils.mock_input(monkeypatch, safepass, inputs)
    
    with caplog.at_level(logging.INFO), pytest.raises(SystemExit) as exit:
        safepass.main()
        
    # DB Creation
    assert 'Encrypted database and salt file created' in caplog.text
    # Entry Insertion
    assert caplog.text.count('New entry created for') == 2
    # Entry Removal
    assert 'Account in Moodle removed' not in caplog.text
    assert 'Account in Moodle under "TestUser" removed' in caplog.text
    # Entry Retrieval / Dump
    assert 'No entries were found for' not in caplog.text
    # Exiting
    assert exit.value.code == 0
    
    inputs = [
        test_utils.TEST_PASSWORD,
        'r', 'Moodle', ' ',
        '6'
    ]
    
    test_utils.mock_input(monkeypatch, safepass, inputs)
    
    with caplog.at_level(logging.INFO), pytest.raises(SystemExit) as exit:
        safepass.main()
        
    assert 'Account in Moodle removed.' in caplog.text
    
def test_master_pwd_change(monkeypatch, caplog):
    new_master_pwd = 'My new master passphrase is this'
    input_pwd_change = [
        test_utils.TEST_PASSWORD, test_utils.TEST_PASSWORD,
        '5', new_master_pwd, new_master_pwd, ' ',
        '6'
    ]
    input_verification = [
        new_master_pwd,
        '6'
    ]
    
    test_utils.new_mock_db(monkeypatch)
    test_utils.mock_input(monkeypatch, safepass, input_pwd_change)
    
    with caplog.at_level(logging.INFO), pytest.raises(SystemExit):
        safepass.main()
        
    assert 'Master password changed, new database and salt files created.' in caplog.text

    test_utils.mock_input(monkeypatch, safepass, input_verification)
    
    with pytest.raises(SystemExit) as exit:
        safepass.main()
        
    assert exit.value.code == 0

def test_backup(monkeypatch, caplog):
    input_creation = [
        test_utils.TEST_PASSWORD, test_utils.TEST_PASSWORD,
        '2', 'Moodle', 'moodle.warwick.ac.uk', 'TestUser', 'MyPaSsWoRd99!', ' ',
        '6'
    ]
    input_validation = [
        test_utils.TEST_PASSWORD,
        '1', 'Moodle', ' ',
        '6'
    ]
    
    test_utils.new_mock_db(monkeypatch)
    test_utils.mock_input(monkeypatch, safepass, input_creation)
    
    with pytest.raises(SystemExit) as exit:
        safepass.main()
    
    assert exit.value.code == 0
        
    test_utils.mock_input(monkeypatch, safepass, input_validation)
    
    with caplog.at_level(logging.INFO), pytest.raises(SystemExit) as exit:
        safepass.main()
        
    assert 'No entries were found for' not in caplog.text
    assert exit.value.code == 0

def test_fetch_nonexistant_account(monkeypatch, caplog):
    inputs = [
        test_utils.TEST_PASSWORD, test_utils.TEST_PASSWORD,
        '1', 'non_existant_service', ' ',
        '4', ' ',
        '6'
    ]
    
    test_utils.new_mock_db(monkeypatch)
    test_utils.mock_input(monkeypatch, safepass, inputs)
    
    with caplog.at_level(logging.INFO), pytest.raises(SystemExit) as exit:
        safepass.main()
        
    assert 'No entries were found for' in caplog.text
    assert 'Database is empty' in caplog.text
    assert exit.value.code == 0