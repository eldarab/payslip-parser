from setuptools import setup

setup(
    name='payslip_parser',
    version='0.1.1',
    description='Parse your payslips from PDFs to pandas dataframes.',
    author='Eldar Abraham',
    url='https://github.com/eldarab/payslip-parser',
    packages=[''],
    license='MIT',
    install_requires=[
        'pandas',
        'pathlib',
        'yaml',
        'pyyaml',
        'fitz>=1.22.3'
    ],
)
