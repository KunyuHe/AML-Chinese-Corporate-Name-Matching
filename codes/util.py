import logging
import os
import webbrowser
from math import atan, pi
from tempfile import NamedTemporaryFile

import pandas as pd
import yaml

from codes import DATA_DIR

logger = logging.getLogger(__name__)


def create_dirs(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


class YamlReader:
    def __init__(self, config_path):
        self.path = config_path
        self.__config = None

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, new_config):
        self.__config = new_config

    def read(self):
        if not os.path.isfile(self.path):
            raise FileNotFoundError(
                f"Configuration file not found at {self.path}.")

        with open(self.path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f.read())

        return self.config


def get_corpnames_full(filename, colname):
    file_path = os.path.join(DATA_DIR, "raw", filename)
    if not os.path.isfile(file_path):
        msg = f"Data not found at {file_path}."
        logger.error(msg)
        raise FileNotFoundError(msg)

    suffix = filename.split(".")[-1]
    if suffix != "xlsx":
        msg = "Data must be in an excel file."
        logger.error(msg)
        raise TypeError(msg)

    df = pd.read_excel(file_path, encoding='utf-8')
    if colname not in df.columns:
        msg = f"{colname} not found in data headers."
        logger.error(msg)
        raise KeyError(msg)

    return df[colname]


def text_sliding_window(text, size):
    n = len(text)
    return [text[i:i + size] for i in range(n - size + 1)]


def arctan_mapping(num):
    return 1 - atan(num) / (pi / 2)


def view_df(df):
    with NamedTemporaryFile(delete=False, suffix='.html', mode='w') as f:
        df.to_html(f)
    webbrowser.open(f.name)


def df_to_csv(df, dir_path, filename, index=False, encoding='utf_8_sig'):
    create_dirs(dir_path)

    if filename.split(".")[-1] != "csv":
        msg = "File name must have the extension .csv."
        logger.error(msg)
        raise TypeError(msg)

    df.to_csv(os.path.join(dir_path, filename), index=index, encoding=encoding)


