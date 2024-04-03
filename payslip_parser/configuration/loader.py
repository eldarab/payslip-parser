import yaml

from payslip_parser.configuration.config import PayslipsParserConfig


def load_config(config_path: str) -> PayslipsParserConfig:
    with open(config_path) as f:
        return PayslipsParserConfig.model_validate(
            yaml.safe_load(f)
        )
