from typing import List, Optional

from pydantic import BaseModel


class RegionBounds(BaseModel):
    """
    Represents the bounds of a region in a payslip.

    Attributes:
        x0: The x-coordinate of the top-left corner.
        y0: The y-coordinate of the top-left corner.
        x1: The x-coordinate of the bottom-right corner.
        y1: The y-coordinate of the bottom-right corner.

    Examples:
        Some explanation of what is possible.

        >>> print("hello!")
        hello!

        Blank lines delimit prose vs. console blocks.

        >>> a = 0
        >>> a += 1
        >>> a
        1
    """
    x0: float
    y0: float
    x1: float
    y1: float


class Region(BaseModel):
    name: str
    is_header: bool
    is_ignore_region: Optional[bool] = False
    bounds: RegionBounds


class PayslipsParserConfig(BaseModel):
    regions: List[Region]
    rtl_payslip: bool
    century_prefix: int
    pages_to_ignore: Optional[List[int]]
