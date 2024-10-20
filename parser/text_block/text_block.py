import abc
from typing import Union

from configuration.config import RegionBounds


class TextBlock(abc.ABC):
    def __init__(self, block_id: int, region_bounds: RegionBounds, region_name: Union[None, str], is_header: bool,
                 text: str):
        self.block_id = block_id
        self.region_bounds = region_bounds
        self.region_name = region_name
        self.is_header = is_header
        self.raw_text = text
        self.parsed_text = self._parse_text(self.raw_text)

    @abc.abstractmethod
    def _parse_text(self, raw_text, *args):
        pass
