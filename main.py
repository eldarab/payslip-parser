import argparse

from tlush_parser import PayslipsParser


def main(payslips_directory_path):
    payslips_parser = PayslipsParser(payslips_directory_path)
    parsed_payslips = payslips_parser.parse_payslips()
    print(parsed_payslips)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--payslips_directory_path', type=str)
    args = parser.parse_args()
    main(args.payslips_directory_path)
