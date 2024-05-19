def validate_integer(string_to_validate: str) -> bool:
    try:
        if str(string_to_validate).isnumeric() and int(string_to_validate):
            return True
    except Exception as e:
        return False
    return False


def validate_float(string_to_validate: str) -> bool:
    try:
        float(string_to_validate)
        return True
    except Exception as e:
        return False


def validate_length(string_to_validate: str, length: int) -> bool:
    if len(str(string_to_validate)) > length:
        return False
    return True


def validate_locked_column_name(string_to_validate: str, locked_columns_list: list) -> bool:
    if string_to_validate in locked_columns_list:
        return False
    return True


def validate_available_currency(string_to_validate: str, available_currency_list: list) -> bool:
    if string_to_validate in available_currency_list:
        return True
    return False
