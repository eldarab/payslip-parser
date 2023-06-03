import os
import re

import fitz
import pandas as pd

RAW_DATA = 'raw_data'
MONTHLY_PAYMENTS = 'monthly_payments'
MONTHLY_REDUCTIONS = 'monthly_reductions'
NET_MONTHLY_PAYMENT = 'net_monthly_payment'
PAYMENTS_DIFFERENCES = 'payments_differences'
REDUCTIONS_DIFFERENCES = 'reductions_differences'
NET_DIFFERENCES = 'net_differences'
TOTAL_TRANSFER_TO_BANK = 'total_transfer_to_bank'


class PayslipsParser:
    regions = {
        RAW_DATA: {'x0': 150, 'x1': 430, 'y0': 140, 'y1': 250},

        MONTHLY_PAYMENTS: {'x0': 220, 'x1': 430, 'y0': 280, 'y1': 390},
        MONTHLY_REDUCTIONS: {'x0': 10, 'x1': 220, 'y0': 280, 'y1': 390},
        NET_MONTHLY_PAYMENT: {'x0': 10, 'x1': 60, 'y0': 385, 'y1': 410},

        PAYMENTS_DIFFERENCES: {'x0': 220, 'x1': 430, 'y0': 420, 'y1': 535},
        REDUCTIONS_DIFFERENCES: {'x0': 10, 'x1': 220, 'y0': 420, 'y1': 535},
        NET_DIFFERENCES: {'x0': 10, 'x1': 60, 'y0': 530, 'y1': 555},

        TOTAL_TRANSFER_TO_BANK: {'x0': 10, 'x1': 70, 'y0': 695, 'y1': 715},
    }
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
        payslip_name = filename[:7] + '__' + filename[-5:-1] + '-' + month
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

    def _get_block_region(self, block):
        for region_name, coordinates_dict in self.regions.items():
            if block['x0'] > coordinates_dict['x0'] and \
                    block['y0'] > coordinates_dict['y0'] and \
                    block['x1'] < coordinates_dict['x1'] and \
                    block['y1'] < coordinates_dict['y1']:
                return region_name
        # raise RuntimeError(f'Region not found for block no. {block["block_no"]}')

    def _payslip_to_blocks(self, payslip_path: str):
        payslip_name = self._get_payslip_name_from_path(payslip_path)
        pdf_blocks = self._load_pdf_to_memory(payslip_path)
        header, body = self._chunkify_pdf(pdf_blocks)
        for block in body:
            block['text'] = self._process_block_text(block['text'], reverse_alphas=True)
            block['region'] = self._get_block_region(block)

        d = {'payslip_name': payslip_name}
        d.update(self._parse_header_blocks(header))
        d['body'] = self._parse_body_blocks(body, filter_rows_without_underscore=True)

        return d

    def parse_payslips(self):
        parsed_payslips = {}

        for payslip_path in self.payslips_paths:
            payslip_blocks = self._payslip_to_blocks(payslip_path)
            payslip_blocks['payslip_path'] = payslip_path
            parsed_payslips[payslip_blocks.pop('payslip_name')] = payslip_blocks

        idx, records = 0, {}
        for payslip in parsed_payslips.values():
            for block in payslip['body']:
                record = self._block_to_record(block)
                if record:
                    record['תאריך תלוש'] = payslip['payslip_date']
                    records[idx] = record
                    idx += 1
        df = pd.DataFrame.from_dict(records, orient='index')

        return parsed_payslips, df

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

    def _parse_body_blocks(self, pdf_blocks, filter_rows_without_underscore=False):
        if filter_rows_without_underscore:
            pdf_blocks = [block for block in pdf_blocks
                          if '_' in block['text']['alphas'] or block['text']['alphas'] == '']

        for block in pdf_blocks:
            block['text']['numbers'] = self._separate_date_from_money(block['text']['numbers'])
            block['text']['numbers'] = self._dash_six_digit_dates(block['text']['numbers'])

        return pdf_blocks

    @staticmethod
    def _process_block_text(text, reverse_alphas=True):
        text = text.strip('\n').replace('\xa0', ' ')

        alphas = ''
        numbers = ''
        for idx, char in enumerate(text):
            if char.isnumeric():
                numbers += char
            elif char == '.' and text[idx - 1].isnumeric() and text[idx + 1].isnumeric():
                numbers += char
            else:
                alphas = char + alphas if reverse_alphas else alphas + char

        return {'alphas': alphas, 'numbers': numbers}

    def _block_to_record(self, block):
        d = {}
        region = block['region']
        alphas = block['text']['alphas']
        numbers = block['text']['numbers']

        if alphas == '':  # no point to add empty line with total region sum
            return None

        if region == RAW_DATA:  # נתונים גולמיים
            d['שם הנתון'] = alphas
            d['ערך הנתון'] = alphas  # TODO
            d['ת. תחילה'] = numbers

        if region == MONTHLY_PAYMENTS:  # תשלומים שוטפים
            d['שם התשלום'] = alphas
            d['סכום קודם (תשלומים שוטפים)'] = None  # TODO
            d['סכום נוכחי (תשלומים שוטפים)'] = numbers

        if region == MONTHLY_REDUCTIONS:  # ניכויים שוטפים
            d['שם הניכוי'] = alphas
            d['סכום קודם (ניכויים שוטפים)'] = None  # TODO
            d['סכום נוכחי (ניכויים שוטפים)'] = numbers

        if region == PAYMENTS_DIFFERENCES:  # הפרשי תשלומים
            d['שם התשלום'] = alphas
            d['תשלום מתאריך'] = numbers.split('__')[2]
            d['תשלום עד תאריך'] = numbers.split('__')[1]
            d['סכום (הפרשי תשלומים)'] = numbers.split('__')[0]

        if region == REDUCTIONS_DIFFERENCES:  # הפרשי ניכויים
            d['שם הניכוי'] = alphas
            d['ניכוי מתאריך'] = numbers.split('__')[2]
            d['ניכוי עד תאריך'] = numbers.split('__')[1]
            d['סכום (הפרשי ניכויים)'] = numbers.split('__')[0]

        return d

    @staticmethod
    def _parse_header_date(text):
        return text.strip('\n').replace(' ', '').replace('/', '-')

    def _parse_header_blocks(self, header):
        d = {}

        for block in header:
            if block['block_no'] != 3:
                block['text'] = self._process_block_text(block['text'])

        # 0th block in header always starts with מ.א., we can drop that
        d['worker_name'] = header[0]['text']['alphas'][4:]
        d['sub_unit'] = header[1]['text']['numbers']
        d['יחתש'] = header[2]['text']['numbers']
        d['payslip_date'] = self._parse_header_date(header[3]['text'])
        d['idf_personal_number'] = header[4]['text']['numbers']
        d['national_id'] = header[5]['text']['numbers']
        d['bank_details'] = {
            'bank_name': header[6]['text']['alphas'],
            'branch_code': header[6]['text']['numbers'],
            'branch_name': header[7]['text']['alphas'],
            'account_no': header[7]['text']['numbers']
        }

        return d
