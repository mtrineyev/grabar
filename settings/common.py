import os

# noinspection PyPackages
from .config_parser import ConfigParser

common_config = ConfigParser('common.yaml')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATE_FORMAT = common_config('date_format')
