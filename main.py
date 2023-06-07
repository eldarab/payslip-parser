import argparse

from idf.idf_payslips_parser import IDFPayslipsParser


def main(payslips_directory_path):
    payslips_parser = IDFPayslipsParser(payslips_directory_path)
    blocks_payslips, df = payslips_parser.parse_payslips()
    df.to_csv('try.csv')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--payslips_directory_path', type=str)
    args = parser.parse_args()
    main(args.payslips_directory_path)
