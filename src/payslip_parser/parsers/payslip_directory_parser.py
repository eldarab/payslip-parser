import abc
import os
import pathlib
from typing import List

import pandas as pd
from pandas import DataFrame

from payslip_parser.payslips.payslip import Payslip
from payslip_parser.parsers.base_payslip_parser import BasePayslipParser


class PayslipDirectoryParser(abc.ABC):
    """
    This class is responsible for parsing a directory containing payslip PDF files and returning a list of parsed payslips.
    It also provides a method to convert the parsed payslips into a DataFrame for further analysis.

    Args:
    payslip_parser (BasePayslipParser): An instance of the BasePayslipParser class, which is responsible for parsing individual payslip PDF files.
    """

    def __init__(self, payslip_parser: BasePayslipParser):
        self.payslip_parser = payslip_parser

    def parse_directory(self, path: str) -> List[Payslip]:
        """
        Parses a directory containing payslip PDF files and returns a list of parsed payslips.

        :param path: The path to the directory containing the payslip PDF files.
        :return: A list of parsed payslips.
        """
        path = pathlib.Path(path)
        assert path.exists()
        assert path.is_dir()
        payslips_paths = [path / filename for filename in os.listdir(path) if filename.endswith('.pdf')]
        parsed_payslips = [self.payslip_parser.parse_payslip(str(p)) for p in payslips_paths]
        return parsed_payslips

    def directory_to_dataframe(self, path: str) -> DataFrame:
        """
        Converts the parsed payslips into a DataFrame for further analysis.

        :param path: The path to the directory containing the payslip PDF files.
        :return: A DataFrame containing the parsed payslip data.
        """
        parsed_payslips = self.parse_directory(path)
        payslip_dfs = []
        for payslip in parsed_payslips:
            records_df = payslip.monthly_records
            records_df = records_df.set_index(payslip.payslip_name + '__' + records_df.index.astype(str))
            records_df['payslip_name'] = payslip.payslip_name
            records_df['payslip_date'] = payslip.payslip_date
            records_df['worker_name'] = payslip.worker_name
            records_df['worker_id'] = payslip.worker_id
            payslip_dfs.append(records_df)
        return pd.concat(payslip_dfs)
