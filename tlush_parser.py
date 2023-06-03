import os
import re

import fitz


class PayslipsParser:
    re_six_digit_date = '(?P<DD>[0-9]{2})(?P<MM>[0-9]{2})(?P<YY>[0-9]{2})'
    re_payment_amount = '(?P<shekels>[0-9]{1,5}).(?P<agorot>[0-9]{2})'
    re_differences = '(?P<from_DD>[0-9]{2})(?P<from_MM>[0-9]{2})(?P<from_YY>[0-9]{2})' \
                     '(?P<to_DD>[0-9]{2})(?P<to_MM>[0-9]{2})(?P<to_YY>[0-9]{2})' + re_payment_amount

    def __init__(self, payslips_directory_path: str):
        self.payslips_directory_path = payslips_directory_path
        self.payslips_paths = [str(self.payslips_directory_path) + "/" + filename
                               for filename in os.listdir(self.payslips_directory_path) if filename.endswith('.pdf')]

    @staticmethod
    def _get_payslip_name_from_path(payslip_path):
        filename = payslip_path.split('/')[-1].split('.')[0]
        month = filename[8:-5] if len(filename[8:-5]) == 2 else '0' + filename[8:-5]  # add leading zero to month
        payslip_name = filename[:7] + '_' + filename[-5:-1] + '-' + month
        return payslip_name

    @staticmethod
    def _block_to_dict(block: tuple) -> dict:
        return {
            'x0': block[0],
            'y0': block[1],
            'x1': block[2],
            'y1': block[3],
            'text': block[4],
            'block_no': block[5],
            'block_type': block[6]
        }

    # noinspection PyUnresolvedReferences
    def _load_pdf_to_memory(self, payslip_path):
        with fitz.open(payslip_path) as pdf:
            blocks = list(pdf.pages(0, 1))[0].get_textpage().extractBLOCKS()
            blocks_dict = [self._block_to_dict(block) for block in blocks]
        return blocks_dict

    @staticmethod
    def _chunkify_pdf(pdf_rows):
        """Returns the PDF divided into body and header"""
        return pdf_rows[:8], pdf_rows[8:]

    def _parse_payslip(self, payslip_path: str):
        payslip_name = self._get_payslip_name_from_path(payslip_path)
        pdf_blocks = self._load_pdf_to_memory(payslip_path)
        for block in pdf_blocks:
            block['text'] = self._separate_alphas_from_numbers(block['text'], reverse_text=True)
        header, body = self._chunkify_pdf(pdf_blocks)

        header = self._parse_blocks(header, filter_rows_without_underscore=False)
        body = self._parse_blocks(body, filter_rows_without_underscore=True)

        return {
            'payslip_name': payslip_name,
            'header': header,
            'body': body,
        }

    def parse_payslips(self) -> dict:
        parsed_payslips = [self._parse_payslip(ps) for ps in self.payslips_paths]
        return {ps.pop('payslip_name'): ps for ps in parsed_payslips}

    def _separate_date_from_money(self, expression: str) -> str:
        m = re.match(self.re_differences, expression)
        if m:
            from_date = f'{m.group("from_DD")}-{m.group("from_MM")}-{m.group("from_YY")}'
            to_date = f'{m.group("to_DD")}-{m.group("to_MM")}-{m.group("to_YY")}'
            total = f'{m.group("shekels")}.{m.group("agorot")}'
            return f'{total}__{to_date}__{from_date}'
        else:
            return expression

    def _dash_six_digit_dates(self, expression: str) -> str:
        """Adds dashes between six digit dates. DDMMYY -> DD-MM-YY"""
        m = re.match(self.re_six_digit_date, expression)
        if len(expression) == 6 and m:
            return f'{m.group("DD")}-{m.group("MM")}-{m.group("YY")}'
        else:
            return expression

    def _parse_blocks(self, pdf_blocks, filter_rows_without_underscore=True):
        if filter_rows_without_underscore:
            pdf_blocks = [block for block in pdf_blocks
                          if '_' in block['text']['alphas'] or block['text']['alphas'] == '']

        for block in pdf_blocks:
            block['text']['numbers'] = self._separate_date_from_money(block['text']['numbers'])
            block['text']['numbers'] = self._dash_six_digit_dates(block['text']['numbers'])

        return pdf_blocks

    @staticmethod
    def _separate_alphas_from_numbers(text, reverse_text=True):
        text = text.strip('\n').replace('\xa0', ' ')

        alphas = ''
        numbers = ''
        for idx, char in enumerate(text):
            if char.isnumeric():
                numbers += char
            elif char == '.' and text[idx - 1].isnumeric() and text[idx + 1].isnumeric():
                numbers += char
            else:
                alphas = char + alphas if reverse_text else alphas + char

        return {'alphas': alphas, 'numbers': numbers}
