import sys, os
import test_utils

import pytest

import safepass

def test_get_new_master_password(monkeypatch, caplog):
    input_sequence = [
        'tooshort',
        '111111111111111', # Fails breach check
        'aValidMasterPassword15', # Passes all checks
        'aValidMasterPassword15' # Confirmation
    ]
    
    monkeypatch.setattr(safepass, 'getpass', test_utils.popper(input_sequence))
    
    with caplog.at_level('WARNING'):
        result_pwd = safepass.get_new_master_password()
    
    assert result_pwd == 'aValidMasterPassword15'
    
    # This sort of string should probably be stored somewhere (not only for testing, also for i18n), but the scope
    # of the project is not that big.
    assert 'Entered password must be at least 15 characters long' in caplog.text
    assert 'Entered password has been breached before' in caplog.text

def test_no_db(monkeypatch):
    monkeypatch.setattr(safepass, 'ENCRYPTED_DB_FILE', test_utils.get_test_db_file('not_existant_db'))
    monkeypatch.setattr(safepass, 'new_database', test_utils.raiser)
    
    with pytest.raises(RuntimeError, match=test_utils.RAISER_EXCEPTION):
        safepass.main()

def test_no_salt(monkeypatch):
    monkeypatch.setattr(safepass, 'ENCRYPTED_DB_FILE', test_utils.get_test_db_file(test_utils.GOOD_DB_FILE))
    monkeypatch.setattr(safepass, 'SALT_FILE', test_utils.get_test_db_file('not_existant_salt'))
    monkeypatch.setattr(safepass, 'offer_new_database', test_utils.raiser)
    
    with pytest.raises(RuntimeError, match=test_utils.RAISER_EXCEPTION):
        safepass.main()

def test_empty_password(monkeypatch):
    input_sequence = [
        '', # No password
        'yes', # Accept new database creation
    ]
    
    monkeypatch.setattr(safepass, 'ENCRYPTED_DB_FILE', test_utils.get_test_db_file(test_utils.GOOD_DB_FILE))
    monkeypatch.setattr(safepass, 'SALT_FILE', test_utils.get_test_db_file(test_utils.GOOD_SALT_FILE))

    monkeypatch.setattr(safepass, 'getpass', test_utils.popper(input_sequence))
    monkeypatch.setattr('builtins.input', test_utils.popper(input_sequence))
    monkeypatch.setattr(safepass, 'new_database', test_utils.raiser)
    
    with pytest.raises(RuntimeError, match=test_utils.RAISER_EXCEPTION):
        safepass.main()
    
    