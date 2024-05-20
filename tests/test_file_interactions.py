import pytest
import pandas as pd
import numpy as np

from file_interactions import FileInteractions


test_filename = 'tests/test_task_data.txt'


@pytest.mark.parametrize('filename, expected', [(test_filename, True), ('tests/test_task_dataa.txt', False)])
def test_file_interactions_initialization(filename, expected):
    fi = FileInteractions(filename)
    assert (True if fi.read_file() else False) == expected


def test_read_file():
    fi = FileInteractions(test_filename)
    header, footer, transactions = fi.read_file()
    header_expected_data = {'Field id': '01', 'Name': 'name', 'Surname': 'surname',
                            'Patronymic': 'patronymic', 'Address': 'address'}
    transactions_expected_data = {'Field id': ['02'] * 12, 'Counter': range(1, 13),
                                  'Amount': [20.0, 120.0, 220.0, 320.0, 420.0, 4212.35, 4142.59,
                                             720.0, 424.87, 920.0, 1020.0, 53.53],
                                  'Currency': ['PLN', 'PLN', 'PLN', 'PLN', 'PLN', 'PLN', 'PLN',
                                               'PLN', 'PLN', 'PLN', 'PLN', 'EUR'],
                                  'Reserved': [''] * 12}
    footer_expected_data = {'Field id': '03', 'Total Counter': '000011',
                            'Control Sum': '000001259334', 'Reserved': 'reserved'}
    header_expected = pd.DataFrame(data=header_expected_data, index=[0])
    transactions_expected = pd.DataFrame(data=transactions_expected_data)
    footer_expected = pd.DataFrame(data=footer_expected_data, index=[0])
    assert header.equals(header_expected) == True
    assert transactions.equals(transactions_expected.astype(object)) == True
    assert footer.equals(footer_expected) == True


def test_add_new_transaction():
    fi = FileInteractions(test_filename)
    _, _, transactions = fi.read_file()
    fi.filename = 'tests/temp_file.txt'
    # Test length of value, must be True, cause firstly its rounded up to 2 digits and then length is validate
    values_dict = {'Amount': 23412.124112313131312312313421411, 'Currency': 'PLN', 'Reserved': ''}
    assert (True if fi.add_new_transaction(values_dict) else False) == True
    _, _, transactions = fi.read_file()
    transactions_expected_data = {'Field id': ['02'] * 13, 'Counter': range(1, 14),
                                  'Amount': [20.0, 120.0, 220.0, 320.0, 420.0, 4212.35, 4142.59,
                                             720.0, 424.87, 920.0, 1020.0, 53.53, 23412.12],
                                  'Currency': ['PLN', 'PLN', 'PLN', 'PLN', 'PLN', 'PLN', 'PLN',
                                               'PLN', 'PLN', 'PLN', 'PLN', 'EUR', 'PLN'],
                                  'Reserved': [''] * 13}
    assert transactions.equals(pd.DataFrame(transactions_expected_data).astype(object)) == True


def test_change_field_value():
    fi = FileInteractions(test_filename)
    _, _, transactions = fi.read_file()
    # Change filename to write in a different one, so one with test data will remain untouched
    fi.filename = 'tests/temp_file.txt'
    # Trying to change value in Amount column
    assert (True if fi.change_field_value(2, '4123.223', transactions.iloc[10]) else False) == True
    # Trying to change locked column value
    assert fi.change_field_value(1, '4123.223', transactions.iloc[10]) == False
    # Trying to change column value in Amount column to not a float or int format
    assert fi.change_field_value(2, 'asd.223', transactions.iloc[10]) == False
    # Trying to change column value in Amount column to very long value
    assert fi.change_field_value(2, '1241241242141231543673526342532352352325.5123', transactions.iloc[10]) == False
    # Trying to change column value in currencies to not allowed currency
    assert fi.change_field_value(3, 'AUS', transactions.iloc[10]) == False
    # Check if all is written back to file
    _, _, transactions = fi.read_file()
    transactions_expected_data = {'Field id': ['02'] * 12, 'Counter': range(1, 13),
                                  'Amount': [20.0, 120.0, 220.0, 320.0, 420.0, 4212.35, 4142.59,
                                             720.0, 424.87, 920.0, 4123.22, 53.53],
                                  'Currency': ['PLN', 'PLN', 'PLN', 'PLN', 'PLN', 'PLN', 'PLN',
                                               'PLN', 'PLN', 'PLN', 'PLN', 'EUR'],
                                  'Reserved': [''] * 12}
    assert transactions.equals(pd.DataFrame(transactions_expected_data).astype(object))
