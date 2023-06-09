from datetime import datetime
from typing import List, Dict, Any

from pandas import DataFrame

from business_logic.payslip_parser import PayslipParser
from business_logic.text_block import TextBlock
from configuration.config import RegionBounds
from idf.idf_text_block import IDFTextBlock


class IDFPayslipParser(PayslipParser):
    def _get_payslip_name(self, payslip_path: str) -> str:
        filename = payslip_path.split('/')[-1].split('.')[0]
        month = filename[8:-5] if len(filename[8:-5]) == 2 else '0' + filename[8:-5]  # add leading zero to month
        payslip_name = filename[:7] + '__' + filename[-5:-1] + '-' + month
        return payslip_name

    def _get_worker_id(self, header_blocks: List[TextBlock]) -> str:
        idf_personal_number_block = header_blocks[4]
        assert idf_personal_number_block.region_name == 'personal_data'
        return idf_personal_number_block.parsed_text['numbers']

    def _get_worker_name(self, header_blocks: List[TextBlock]) -> str:
        worker_name_block = header_blocks[0]
        assert worker_name_block.region_name == 'to'
        return worker_name_block.parsed_text['alphas'][4:]  # get rid of מ.א. prefix

    def _get_payslip_date(self, header_blocks: List[TextBlock]) -> datetime:
        payslip_date_block = header_blocks[3]
        assert payslip_date_block.region_name == 'payslip_date'
        return datetime(
            year=int(payslip_date_block.parsed_text['numbers'][-4:]),
            month=int(payslip_date_block.parsed_text['numbers'][:-4]),
            day=1
        )

    def _get_additional_metadata(self, header_blocks: List[TextBlock]) -> Any:
        """todo: subunit, יחתש, national_id, bank_details"""
        payment_unit_block = header_blocks[2]
        assert payment_unit_block.region_name == 'to'

        national_id_block = header_blocks[5]
        assert national_id_block.region_name == 'personal_data'

        bank_name_block = header_blocks[6]
        account_details_block = header_blocks[7]
        assert bank_name_block.region_name == account_details_block.region_name == 'bank_details'

        return {
            'payment_unit': payment_unit_block.parsed_text['numbers'],  # יחתש
            'national_id': national_id_block.parsed_text['numbers'][:9],  # remove יחתש suffix, if exists
            'bank_details': {
                'bank_name': bank_name_block.parsed_text['alphas'],
                'branch_code': bank_name_block.parsed_text['numbers'],
                'branch_name': account_details_block.parsed_text['alphas'],
                'account_number': account_details_block.parsed_text['numbers']
            }
        }



    def _get_payslip_records(self, body_blocks: List[TextBlock]) -> DataFrame:
        pass

    def _instantiate_text_block(self, block_id: int, region_bounds: RegionBounds, region_name: str, is_header: bool,
                                text: str) -> TextBlock:
        return IDFTextBlock(block_id, region_bounds, region_name, is_header, text)
