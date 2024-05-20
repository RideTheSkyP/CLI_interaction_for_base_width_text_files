import pytest

import custom_validators


test_values = ['USD', 'abc', '123', '12.21', '12.eqe', 123, 123.21]
integer_expected_answer = [False, False, True, False, False, True, False]
float_expected_answer = [False, False, True, True, False, True, True]
test_value_lengths = [2, 3, 4, 20, 0, 5]
length_expected_answer = [False, True, True, True, False, True, False]
column_names = [123, 'abc', '123']
locked_column_names_expected_answer = [False, True, True, False, False, True, False]
available_currencies = ['USD', 'EUR', 'PLN']
available_currencies_expected_answer = [True, False, False, False, False, False, False]


@pytest.mark.parametrize('test_value, expected', zip(test_values, integer_expected_answer))
def test_validate_integer(test_value, expected):
    assert custom_validators.validate_integer(test_value) == expected


@pytest.mark.parametrize('test_value, expected', zip(test_values, float_expected_answer))
def test_validate_float(test_value, expected):
    assert custom_validators.validate_float(test_value) == expected


@pytest.mark.parametrize('test_value, test_value_length, expected', zip(test_values, test_value_lengths, length_expected_answer))
def test_validate_length(test_value, test_value_length, expected):
    assert custom_validators.validate_length(test_value, test_value_length) == expected


@pytest.mark.parametrize('test_value, expected', zip(test_values, locked_column_names_expected_answer))
def test_validate_locked_column_name(test_value, expected):
    assert (test_value in column_names) == expected


@pytest.mark.parametrize('test_value, expected', zip(test_values, available_currencies_expected_answer))
def test_validate_available_currency(test_value, expected):
    assert (test_value in available_currencies) == expected
