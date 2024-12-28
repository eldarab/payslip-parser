import abc
from datetime import date
from typing import Any, List, Dict

import fitz
from pandas import DataFrame

from payslip_parser.configuration.config import RegionBounds
from payslip_parser.payslips import Payslip
from payslip_parser.text_blocks.base_text_block import BaseTextBlock


class BasePayslipParser(abc.ABC):
    """
    Abstract base class for parsing payslip documents.

    This class provides a foundation for extracting data from PDF payslip files.
    It organizes the data into header and body blocks and processes them into
    structured records.

    Methods:
        parse_payslip(payslip_path: str) -> Payslip:
            Parses a payslip PDF and returns a `Payslip` object.
    """

    def parse_payslip(self, payslip_path: str) -> Payslip:
        """
        Parses a payslip PDF file and extracts structured data into a Payslip object.

        :param payslip_path: The file path to the payslip PDF.
        :type payslip_path: str
        :return: A Payslip object containing parsed information.
        :rtype: Payslip

        Workflow:
            1. Opens the PDF file using `fitz`.
            2. Iterates through each page and extracts text blocks.
            3. Identifies relevant regions using `_get_region_details` and
               instantiates text blocks.
            4. Separates text blocks into header and body blocks.
            5. Converts body blocks into structured records using `_get_payslip_records`.
            6. Populates and returns a `Payslip` object.

        Notes:
            - Header blocks contain descriptive metadata, such as worker name and ID.
            - Body blocks contain detailed payslip records, such as salary information.

        :raises RuntimeError: If a region cannot be identified within the defined regions.

        Example:
            >>> parser = MyPayslipParser()
            >>> payslip = parser.parse_payslip("example_payslip.pdf")
        """
        ...
        # noinspection PyUnresolvedReferences
        pdf = fitz.open(payslip_path)
        text_blocks = []
        for page_idx, page in enumerate(pdf):
            if self.config.pages_to_ignore is not None and page_idx in self.config.pages_to_ignore:
                continue
            for pdf_block in page.get_textpage().extractBLOCKS():
                region_bounds = RegionBounds(
                    x0=pdf_block[0],
                    y0=pdf_block[1],
                    x1=pdf_block[2],
                    y1=pdf_block[3]
                )
                region_details = self._get_region_details(region_bounds)
                if region_details is not None:
                    region_name, is_header = region_details
                    text_block = self._instantiate_text_block(
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

    def _get_payslip_records(self, body_blocks: List[BaseTextBlock]) -> DataFrame:
        records = []
        for block in body_blocks:
            record = self._body_block_to_record(block)
            if record:
                records.append(record)
        df = DataFrame(records)
        df = df.dropna(how='all')
        df = df.reset_index(drop=True)
        return df

    def _get_region_details(self, bounds: RegionBounds) -> (str, bool):
        for region in self.config.regions:
            if bounds.x0 > region.bounds.x0 and \
                    bounds.y0 > region.bounds.y0 and \
                    bounds.x1 < region.bounds.x1 and \
                    bounds.y1 < region.bounds.y1:
                if region.is_ignore_region:
                    return None
                else:
                    return region.name, region.is_header
        raise RuntimeError(f'Unidentified region: {bounds}')

    @abc.abstractmethod
    def _get_payslip_name(self, payslip_path: str) -> str:
        pass

    @abc.abstractmethod
    def _get_worker_id(self, header_blocks: List[BaseTextBlock]) -> str:
        pass

    @abc.abstractmethod
    def _get_worker_name(self, header_blocks: List[BaseTextBlock]) -> str:
        pass

    @abc.abstractmethod
    def _get_payslip_date(self, header_blocks: List[BaseTextBlock]) -> date:
        pass

    def _get_additional_metadata(self, header_blocks: List[BaseTextBlock]) -> Any:
        pass

    @abc.abstractmethod
    def _instantiate_text_block(self, block_id: int, region_bounds: RegionBounds, region_name: str, is_header: bool,
                                text: str) -> BaseTextBlock:
        pass

    @abc.abstractmethod
    def _body_block_to_record(self, block: BaseTextBlock) -> Dict:
        pass
