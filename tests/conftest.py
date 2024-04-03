import os
import pathlib
from typing import List

import pytest

from payslip_parser import load_config, IDFPayslipParser

ROOT_PATH = pathlib.Path("C:\\Users\\Eldar-Desktop\\PycharmProjects\\payslip-parser")  # set this to project's root
SOURCE_DIR = ROOT_PATH / "payslip_parser"
EXAMPLE_PAYSLIPS_DIR = ROOT_PATH / "example_payslips"


@pytest.fixture
def idf_payslip_parser() -> IDFPayslipParser:
    """A fixture for the IDFPayslipParser"""

    idf_payslip_parser_config = load_config(f"{SOURCE_DIR}/configuration/idf_payslip_config.yaml")
    return IDFPayslipParser(idf_payslip_parser_config)


@pytest.fixture
def idf_payslips_paths() -> List[str]:
    """A fixture for getting all IDF payslips paths"""

    payslips_filenames = os.listdir(EXAMPLE_PAYSLIPS_DIR)
    payslips_paths = [f"{EXAMPLE_PAYSLIPS_DIR}/{filename}" for filename in payslips_filenames]

    return payslips_paths


@pytest.fixture
def idf_payslip_from_2023_path() -> str:
    """A fixture for getting the last IDF payslip path"""

    return f"{EXAMPLE_PAYSLIPS_DIR}/86901611320231.pdf"
