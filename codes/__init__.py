import os

API_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_DIR = os.path.join(API_DIR, os.pardir, 'config')
DATA_DIR = os.path.join(API_DIR, os.pardir, 'data')
MODEL_DIR = os.path.join(API_DIR, os.pardir, 'models')
REPORT_DIR = os.path.join(API_DIR, os.pardir, 'reports')
