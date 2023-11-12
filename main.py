import argparse

from payslip_parser import load_config, IDFPayslipParser, PayslipDirectoryParser


def main(args):
    config = load_config(args.config_path)
    idf_payslip_parser = IDFPayslipParser(config)
    idf_directory_parser = PayslipDirectoryParser(idf_payslip_parser)
    df = idf_directory_parser.directory_to_dataframe(args.directory_path)
    print(df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--payslip_path', type=str,
                        default='H:/My Drive/Personal/Finance/Paychecks/IDF/86901611520231.pdf')
    parser.add_argument('--directory_path', type=str, default='H:/My Drive/Personal/Finance/Paychecks/IDF')
    parser.add_argument('--config_path', type=str, default='./payslip_parser/configuration/idf_payslip_config.yaml')
    main_args = parser.parse_args()

    main(main_args)
