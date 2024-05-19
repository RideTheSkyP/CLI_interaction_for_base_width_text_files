import pandas as pd
from typing import Union

import custom_validators
from colored_logger import logger


class FileInteractions:
    def __init__(self, filename: str):
        self.filename = filename
        self.file_lines = []
        self.total_counter = 0
        self.max_lengths_dict = {}
        self.header_positions = (2, 30, 60, 90, 120)
        self.transaction_positions = (2, 8, 20, 23, 120)
        self.footer_positions = (2, 8, 20, 120)
        self.header = pd.DataFrame([], columns=['Field id', 'Name', 'Surname', 'Patronymic', 'Address'])
        self.transactions = pd.DataFrame([], columns=['Field id', 'Counter', 'Amount', 'Currency', 'Reserved'])
        self.footer = pd.DataFrame([], columns=['Field id', 'Total Counter', 'Control Sum', 'Reserved'])
        self.locked_to_write_access_fields = ['Field id', 'Counter', 'Total Counter', 'Control Sum']
        self.field_fillers = {'Counter': '0', 'Amount': '0', 'Field id': '0', 'Total Counter': '0', 'Control Sum': '0',
                              'Name': ' ', 'Surname': ' ', 'Patronymic': ' ', 'Address': ' ',
                              'Currency': ' ', 'Reserved': ' '}
        self.availabe_currencies= ['USD', 'EUR', 'PLN']
        self.set_lengths_for_fields()

    def set_lengths_for_fields(self) -> dict:
        self.max_lengths_dict.update(self.calculate_distance_for_fields(self.header, self.header_positions))
        self.max_lengths_dict.update(self.calculate_distance_for_fields(self.transactions, self.transaction_positions))
        self.max_lengths_dict.update(self.calculate_distance_for_fields(self.footer, self.footer_positions))
        return self.max_lengths_dict

    def calculate_distance_for_fields(self, fields: list, positions: tuple) -> dict[str: int]:
        length_dict = {}
        prev_position = 0
        for column, position in zip(fields, positions):
            length_dict[column] = position - prev_position
            prev_position = position
        return length_dict

    def split_string_by_positions(self, text: str, positions: tuple) -> list[str]:
        prev_position = 0
        split_string = []
        for position in positions:
            split_string.append(text[prev_position:position].strip())
            prev_position = position
        return split_string

    def read_file(self) -> Union[tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame], bool]:
        try:
            with open(self.filename, 'r') as f:
                self.file_lines = f.readlines()
            self.header = pd.DataFrame([self.split_string_by_positions(self.file_lines[0], self.header_positions)],
                                       columns=self.header.columns)
            self.footer = pd.DataFrame([self.split_string_by_positions(self.file_lines[-1], self.footer_positions)],
                                       columns=self.footer.columns)
            self.transactions = pd.DataFrame(list(map(lambda transaction: self.split_string_by_positions(transaction, self.transaction_positions), self.file_lines[1:-1])),
                                             columns=self.transactions.columns)
            self.transactions.loc[:, 'Counter'] = self.transactions['Counter'].apply(int)
            self.transactions.loc[:, 'Amount'] = self.transactions['Amount'].apply(lambda x: int(x)/100)
            self.total_counter = len(self.transactions)
            return self.header, self.footer, self.transactions
        except FileNotFoundError as fnfe:
            logger.error(f'Check if file path is correct {self.filename}')
        except Exception as e:
            logger.error(f'Check if file structure is not corrupted: {e}')
        return False

    def format_value(self, row: pd.Series) -> str:
        formatted_row = ''
        for col, value in row.items():
            filler = self.field_fillers.get(col)
            formatted_value = f'{str(value)[:self.max_lengths_dict[col]]:{filler}>{self.max_lengths_dict[col]}}'
            formatted_row += formatted_value
        return f'{formatted_row}\n'

    def write_to_file(self) -> int:
        try:
            header = self.header.copy()
            transactions = self.transactions.copy()
            footer = self.footer.copy()
            transactions['Amount'] = self.transactions['Amount'].apply(lambda x: int(x * 100))
            footer['Total Counter'] = self.total_counter
            footer['Control Sum'] = int(self.transactions['Amount'].sum() * 100)

            with open(self.filename, 'w') as f:
                for df in [header, transactions, footer]:
                    formatted_lines = df.apply(lambda row: self.format_value(row), axis=1)
                    for line in formatted_lines:
                        f.write(line)
        except Exception as e:
            logger.error(f'{e}')
            return False
        return 'Successfuly written to file'

    def add_new_transaction(self, values_dict: dict) -> int:
        for key in values_dict.keys():
            values_dict[key] = self.run_validators(key, values_dict[key])
        if False in values_dict.values():
            return -1
        values_dict['Field id'] = '02'
        values_dict['Counter'] = len(self.transactions) + 1
        self.transactions.loc[len(self.transactions)] = values_dict
        return self.write_to_file()

    def change_field_value(self, field_choice: int, field_value: str, field: pd.Series) -> int:
        field_value = self.run_validators(field.index[field_choice], field_value)
        if field_value:
            field.iloc[field_choice] = field_value
            logger.info(f'Value in column "{field.index[field_choice]}" changed successfuly to "{field_value}"')
            return self.write_to_file()
        return field_value

    def run_validators(self, field_column: str, field_value: str) -> Union[bool, float, str]:
        if not custom_validators.validate_locked_column_name(field_column, self.locked_to_write_access_fields):
            logger.error(f'Validation error: Trying to change value in locked column "{field_column}"\n')
            return False

        if field_column == 'Amount':
            if not custom_validators.validate_float(field_value):
                logger.error(f'Validation error: "{field_value}" is not a float\n')
                return False
            field_value = round(float(field_value), 2)
        elif field_column == 'Currency':
            if not custom_validators.validate_available_currency(field_value, self.availabe_currencies):
                logger.error(f'Validation error: Currency "{field_value}" is not available. '
                             f'Available currencies: {self.availabe_currencies}\n')
                return False
        max_length_for_field = self.max_lengths_dict.get(field_column)
        if not custom_validators.validate_length(str(field_value), max_length_for_field):
            logger.error(f'Validation error: "{field_value}" contains more than {max_length_for_field} characters\n')
            return False
        return field_value
