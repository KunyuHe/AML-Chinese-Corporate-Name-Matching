import logging
import os

import pandas as pd
import yaml

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


def get_corpnames_full(file_path, colname):
    if not os.path.isfile(file_path):
        msg = f"Data not found at {file_path}."
        logger.error(msg)
        raise FileNotFoundError(msg)

    filename = os.path.split(file_path)[-1]
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
