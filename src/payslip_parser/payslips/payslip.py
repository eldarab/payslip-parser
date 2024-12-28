from datetime import date
from typing import Any

from pandas import DataFrame


class Payslip:
    """
    Represents a Payslip object containing all the necessary information about a worker's payslip.

    Attributes:
        payslip_name (str): The name of the payslip.
        payslip_date (date): The date of the payslip.
        worker_name (str): The name of the worker.
        worker_id (str): The unique identifier of the worker.
        additional_metadata (Any): Additional metadata related to the payslip.
        monthly_records (DataFrame): A DataFrame containing the monthly records of the worker's payslip.

    Methods:
        __init__(payslip_name: str, payslip_date: date, worker_name: str, worker_id: str, additional_metadata: Any, payslip_records: DataFrame) -> None:
            Initializes a new Payslip object with the provided information.
    """

    def __init__(
            self,
            payslip_name: str,
            payslip_date: date,
            worker_name: str,
            worker_id: str,
            additional_metadata: Any,
            payslip_records: DataFrame
    ) -> None:
        """
        Initializes a new Payslip object with the provided information.

        Args:
            payslip_name (str): The name of the payslip.
            payslip_date (date): The date of the payslip.
            worker_name (str): The name of the worker.
            worker_id (str): The unique identifier of the worker.
            additional_metadata (Any): Additional metadata related to the payslip.
            payslip_records (DataFrame): A DataFrame containing the monthly records of the worker's payslip.

        Returns:
            None: This method does not return any value. It initializes a new Payslip object.
        """
        self.payslip_name = payslip_name
        self.payslip_date = payslip_date
        self.worker_name = worker_name
        self.worker_id = worker_id
        self.additional_metadata = additional_metadata
        self.monthly_records = payslip_records
