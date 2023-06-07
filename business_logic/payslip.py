from datetime import datetime
from typing import Any

from pandas import DataFrame


class Payslip:
    def __init__(self, payslip_name: str, payslip_date: datetime, worker_name: str, worker_id: str,
                 additional_metadata: Any, payslip_records: DataFrame):
        self.payslip_name = payslip_name
        self.payslip_date = payslip_date
        self.worker_name = worker_name
        self.worker_id = worker_id
        self.additional_metadata = additional_metadata
        self.monthly_records = payslip_records
