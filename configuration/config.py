from typing import Dict, AnyStr, List

from pydantic import BaseModel


class RegionBounds(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class Region(BaseModel):
    name: str
    is_header: bool
    bounds: RegionBounds


class PayslipsParserConfig(BaseModel):
    regions: List[Region]
    regular_expressions: Dict[str, AnyStr]
    rtl_payslip: bool
    century_prefix: int
