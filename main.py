import argparse

from parser.payslip_directory_parser.payslip_directory_parser import PayslipDirectoryParser
from configuration.loader import load_config
from parser.payslip_parser.idf_payslip_parser import IDFPayslipParser


def main(args):
    config = load_config(args.config_path)
    idf_payslip_parser = IDFPayslipParser(config)
    idf_directory_parser = PayslipDirectoryParser(idf_payslip_parser)
    df = idf_directory_parser.directory_to_dataframe(args.directory_path)
    print(df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--payslip_path', type=str,
                        default='I:/My Drive/Personal/Finance/Paychecks/IDF/86901611520231.pdf')
    parser.add_argument('--directory_path', type=str, default='I:/My Drive/Personal/Finance/Paychecks/IDF')
    parser.add_argument('--config_path', type=str, default='./config.yaml')
    main_args = parser.parse_args()

    main(main_args)
