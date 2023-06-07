from datetime import datetime
from typing import List

from pandas import DataFrame

from business_logic.payslip_parser import PayslipParser
from business_logic.text_block import TextBlock


class IDFPayslipParser(PayslipParser):
    def _get_payslip_name(self, payslip_path: str) -> str:
        filename = payslip_path.split('/')[-1].split('.')[0]
        month = filename[8:-5] if len(filename[8:-5]) == 2 else '0' + filename[8:-5]  # add leading zero to month
        payslip_name = filename[:7] + '__' + filename[-5:-1] + '-' + month
        return payslip_name

    def _get_worker_id(self, header_blocks: List[TextBlock]) -> str:
        pass

    def _get_worker_name(self, header_blocks: List[TextBlock]) -> str:
        pass

    def _get_payslip_date(self, header_blocks: List[TextBlock]) -> datetime:
        pass

    def _get_payslip_records(self, body_blocks: List[TextBlock]) -> DataFrame:
        pass