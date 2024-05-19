import pandas as pd

from colored_logger import logger
from cli_interactions import user_interaction
from file_interactions import FileInteractions


def main():
    print('Welcome to the CLI tool.')
    try:
        fi = FileInteractions('task_data.txt')
        header, footer, transactions = fi.read_file()
        user_interaction(fi, header, footer, transactions)
    except Exception as e:
        logger.error(f'{e}')


if __name__ == '__main__':
    main()