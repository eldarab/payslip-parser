from typing import List, Optional

from pydantic import BaseModel


class RegionBounds(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class Region(BaseModel):
    name: str
    is_header: bool
    is_ignore_region: Optional[bool]
    bounds: RegionBounds


class PayslipsParserConfig(BaseModel):
    regions: List[Region]
    rtl_payslip: bool
    century_prefix: int
    pages_to_ignore: Optional[List[int]]
