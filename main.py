import argparse

from configuration.loader import load_config
from idf.idf_payslip_parser import IDFPayslipParser


def main(args):
    config = load_config(args.config_path)
    idf_payslip_parser = IDFPayslipParser(config)
    parsed_payslip = idf_payslip_parser.parse_payslip(args.payslip_path)
    print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--payslip_path', type=str, default='./86901611520231.pdf')
    parser.add_argument('--config_path', type=str, default='./idf/config.yaml')
    main_args = parser.parse_args()

    main(main_args)
