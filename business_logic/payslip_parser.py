import abc
from datetime import datetime
from typing import Any

import fitz
from pandas import DataFrame

from business_logic.payslip import Payslip
from business_logic.text_block import TextBlock
from configuration.config import PayslipsParserConfig, RegionBounds


class PayslipParser(abc.ABC):
    """An ABC for parsing a single payslip"""

    def __init__(self, config: PayslipsParserConfig):
        self.config = config

    def parse_payslip(self, payslip_path: str) -> Payslip:
        with fitz.open(payslip_path) as pdf:
            text_blocks = []
            for page in pdf.pages:
                for pdf_block in page.get_textpage().extractBLOCKS():
                    region_bounds = RegionBounds(
                        x0=pdf_block[0],
                        y0=pdf_block[1],
                        x1=pdf_block[2],
                        y1=pdf_block[3]
                    )
                    region_name = self._identify_region(region_bounds)
                    is_header = region_name in self.config.header_regions
                    text_block = TextBlock(
                        block_id=pdf_block[5],
                        region_bounds=region_bounds,
                        region_name=region_name,
                        is_header=is_header,
                        text=pdf_block[4]
                    )
                    text_blocks.append(text_block)

        # header blocks are descriptive of the payslip in general, for example worker name
        header_blocks = [block for block in text_blocks if block.is_header]

        # body blocks will eventually become payslip records, for example base monthly salary
        body_blocks = [block for block in text_blocks if not block.is_header]

        return Payslip(
            payslip_name=self._get_payslip_name(payslip_path),
            payslip_date=self._get_payslip_date(header_blocks),
            worker_id=self._get_worker_id(header_blocks),
            worker_name=self._get_worker_name(header_blocks),
            additional_metadata=self._get_additional_metadata(header_blocks),
            payslip_records=self._get_payslip_records(body_blocks)
        )

    @abc.abstractmethod
    def _get_payslip_name(self, payslip_path) -> str:
        pass

    @abc.abstractmethod
    def _get_worker_id(self, header_blocks) -> str:
        pass

    @abc.abstractmethod
    def _get_worker_name(self, header_blocks) -> str:
        pass

    @abc.abstractmethod
    def _get_payslip_date(self, header_blocks) -> datetime:
        pass

    def _get_additional_metadata(self, header_blocks) -> Any:
        pass

    @abc.abstractmethod
    def _get_payslip_records(self, body_blocks) -> DataFrame:
        pass

    def _identify_region(self, region_bounds: RegionBounds) -> str:
        for region_name, region in self.config.regions.items():
            if region_bounds.x0 > region.x0 and \
                    region_bounds.y0 > region.y0 and \
                    region_bounds.x1 < region.x1 and \
                    region_bounds.y1 < region.y1:
                return region_name
        raise RuntimeError('Unidentified region.')
