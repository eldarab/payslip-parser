from payslip_parser import IDFPayslipParser


def test_idf_payslip_parser(idf_payslip_parser: IDFPayslipParser, idf_payslip_from_2023_path) -> None:
    # arrange
    pass

    # act
    payslip = idf_payslip_parser.parse_payslip(idf_payslip_from_2023_path)

    # assert
    assert payslip.payslip_date.year == 2023
