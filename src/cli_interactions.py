import logging
import pandas as pd
from typing import Any, Union

from colored_logger import logger
from file_interactions import FileInteractions


def input_interaction_handler(input_text: str, success_thresholds, return_option: Any=-1, cast_function=str) -> Union[int, str]:
    try:
        input_answer = input(input_text)
        if not input_answer:
            return input_interaction_handler(input_text, success_thresholds, return_option, cast_function)
        casted_input_answer = cast_function(input_answer)
        if casted_input_answer == return_option:
            return 'return'
        elif casted_input_answer not in success_thresholds:
            raise Exception(f'Please enter right value in {success_thresholds}')
        return casted_input_answer
    except Exception as e:
        logger.error(f'{e}')
    return 'error'


def create_help_text_for_transactions(text: str, transactions: list, step: int = 1) -> tuple[str, list]:
    split_transactions = []
    transactions_range_choice = 0
    counter = -1
    input_text = f'{counter}. Return\n'

    for i in range(0, len(transactions), step):
        counter += 1
        split_transactions.append(transactions[i:i+step])
        input_text += text.format(counter=counter, start=i, stop=i+step)

    return input_text, split_transactions


def transactions_input(input_text: str, transactions_range_len: int) -> int:
    transactions_range_choice = input_interaction_handler(input_text, range(-1, transactions_range_len),
                                                          return_option=-1, cast_function=int)
    if transactions_range_choice == 'error':
        return transactions_input(input_text, transactions_range_len)
    return transactions_range_choice


def get_index_from_transactions_chunk(input_text: str, transactions_range_indexes: pd.RangeIndex, chunk_size: int) -> int:
    one_transaction_choice = input_interaction_handler(input_text, transactions_range_indexes,
                                                       return_option=-1, cast_function=int)
    if one_transaction_choice == 'error':
        return get_index_from_transactions_chunk(input_text, transactions_range_indexes, chunk_size)
    elif one_transaction_choice == 'return':
        return one_transaction_choice
    index_within_chunk = one_transaction_choice % chunk_size
    return index_within_chunk


def change_values_in_header_or_footer(file_interactions: FileInteractions, header_or_footer: pd.DataFrame) -> int:
    input_text = f'You are about to change following line:\n' \
                 f'{header_or_footer}\n\n' \
                 'Select field which you want to change:\n' \
                 '-1. Return\n'
    header_or_footer_row = header_or_footer.iloc[0]
    field_columns = [f'{index}. {column}\n' for index, column in enumerate(header_or_footer_row.index)]
    input_text += ''.join(field_columns)
    field_choice = input_interaction_handler(input_text, range(-1, len(header_or_footer_row.index)),
                                             return_option=-1, cast_function=int)

    if field_choice == 'return':
        return ''

    field_value = input(f'Please enter value for {header_or_footer_row.index[field_choice]}:\n'
                        f'Type return to return\n')
    if field_value == 'return' or not file_interactions.change_field_value(field_choice, field_value, header_or_footer_row):
        return change_values_in_header_or_footer(file_interactions, header_or_footer)

    return field_value


def interactions_with_transactions(file_interactions: FileInteractions, transactions: pd.DataFrame, choice: int = 1) -> str:
    # Split every 200 transaction to make choice output more human readable
    chunk_size = 200
    input_text, transactions_range = create_help_text_for_transactions('{counter}. Display transactions from {start} to {stop}\n',
                                                                       transactions, step=chunk_size)

    transactions_range_choice = transactions_input(input_text, len(transactions_range))
    if transactions_range_choice == 'return':
        return ''
    print(transactions_range[transactions_range_choice])
    transactions_range_indexes = transactions_range[transactions_range_choice].index

    if choice == 1:
        index_within_chunk = get_index_from_transactions_chunk(f'Select one transaction to display by its '
                                                               f'index (first column)[{transactions_range_indexes[0]}-'
                                                               f'{transactions_range_indexes[-1]}]:\n-1. Return\n',
                                                               transactions_range_indexes,
                                                               chunk_size)
        if index_within_chunk == 'return':
            return interactions_with_transactions(file_interactions, transactions, choice)
        transaction = transactions_range[transactions_range_choice].iloc[index_within_chunk]
        print(transaction)
    elif choice == 2:
        index_within_chunk = get_index_from_transactions_chunk(f'Select transaction which you want to '
                                                               f'change[{transactions_range_indexes[0]}-'
                                                               f'{transactions_range_indexes[-1]}]:\n-1. Return\n',
                                                               transactions_range_indexes,
                                                               chunk_size)
        if index_within_chunk == 'return':
            return interactions_with_transactions(file_interactions, transactions, choice)
        transaction = transactions_range[transactions_range_choice].iloc[index_within_chunk]
        print(transaction)
        transaction_columns = [f'{index}. {column}\n' for index, column in enumerate(transaction.index)]
        field_input_text = 'Select field which you want to change:\n' \
                           '-1. Return\n'
        field_input_text += ''.join(transaction_columns)
        transaction_field_choice = input_interaction_handler(field_input_text, range(-1, len(transaction.index)),
                                                             return_option=-1, cast_function=int)

        if transaction_field_choice == 'return':
            return interactions_with_transactions(file_interactions, transactions, choice)

        transaction_field_value = input(f'Please enter value for {transaction.index[transaction_field_choice]}:\n'
                                        f'Type return to return\n')
        if transaction_field_value == 'return' or not file_interactions.change_field_value(transaction_field_choice,
                                                                                           transaction_field_value,
                                                                                           transaction):
            return interactions_with_transactions(file_interactions, transactions, choice)
    return ''


def get_value_interaction(file_interactions, header: pd.DataFrame, footer: pd.DataFrame, transactions: pd.DataFrame) -> int:
    input_text = 'Select field to get values:\n' \
                 '-1. Return\n' \
                 '0. Header\n' \
                 '1. Transactions\n' \
                 '2. Footer\n'
    user_inp = input_interaction_handler(input_text, range(-1, 3), return_option=-1, cast_function=int)
    if user_inp == 'return':
        return ''
    elif user_inp == 0:
        return str(header)
    elif user_inp == 1:
        return interactions_with_transactions(file_interactions, transactions, choice=1)
    elif user_inp == 2:
        return str(footer)
    return get_value_interaction(file_interactions, header, footer, transactions)



def add_new_transaction_interaction(file_interactions: FileInteractions, transactions: pd.DataFrame) -> int:
    values_dict = {}
    for column in transactions.columns[-3:]:
        values_dict[column] = input(f'Provide value for "{column}":\n')
    return file_interactions.add_new_transaction(values_dict)


def change_values_interaction(file_interactions, header: pd.DataFrame, footer: pd.DataFrame, transactions: pd.DataFrame) -> int:
    input_text = 'Select field to change values:\n' \
                 '-1. Return\n' \
                 '0. Header\n' \
                 '1. Transactions\n' \
                 '2. Footer\n'
    user_inp = input_interaction_handler(input_text, range(-1, 3), return_option=-1, cast_function=int)
    if user_inp == 'return':
        return ''
    elif user_inp == 0:
        result = change_values_in_header_or_footer(file_interactions, header)
    elif user_inp == 1:
        result = interactions_with_transactions(file_interactions, transactions, choice=2)
    elif user_inp == 2:
        result = change_values_in_header_or_footer(file_interactions, footer)
    return change_values_interaction(file_interactions, header, footer, transactions)


def user_interaction(file_interactions: FileInteractions, header: pd.DataFrame, footer: pd.DataFrame, transactions: pd.DataFrame) -> int:
    result = ''
    user_inp = input('Please select number from the menu:\n'
                     '1. Get the value of specified field\n'
                     '2. Change field values\n'
                     '3. Add new transaction\n'
                     '4. Exit\n')

    if (not user_inp) or (not user_inp.isnumeric()) or (int(user_inp) not in range(1, 5)):
        logger.error('Please enter a correct number')
        return user_interaction(file_interactions, header, footer, transactions)

    user_inp = int(user_inp)
    if user_inp == 1:
        result = get_value_interaction(file_interactions, header, footer, transactions)
    elif user_inp == 2:
        result = change_values_interaction(file_interactions, header, footer, transactions)
    elif user_inp == 3:
        result = add_new_transaction_interaction(file_interactions, transactions)
    elif user_inp == 4:
        exit(0)
    print(f'\n{result}\n' if result else result)
    return user_interaction(file_interactions, header, footer, transactions)
