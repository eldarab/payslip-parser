from typing import Dict, AnyStr, List

from pydantic import BaseModel


class RegionBounds(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class PayslipsParserConfig(BaseModel):
    regions: Dict[str, RegionBounds]
    regular_expressions: Dict[str, AnyStr]
    is_rtl_payslip: bool
    header_regions: List[str]
