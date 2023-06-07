import abc


class PayslipDirectoryParser(abc.ABC):
    """An ABC for parsing a directory of payslips of the same format"""

    @abc.abstractmethod
    def _parse_payslip(self, payslip):
        """Parses a single payslip"""

    def parse_directory(self, directory):
        return [self._parse_payslip(p) for p in directory]
