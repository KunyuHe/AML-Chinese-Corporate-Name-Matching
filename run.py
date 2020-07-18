import argparse
import logging.config
import os

from api import CONFIG_DIR, DATA_DIR
from api.extract.extractor import JiebaExtractor, get_corpnames_partial
from api.utils.util import YamlReader, get_corpnames_full

parser = argparse.ArgumentParser()
parser.add_argument('--log_config',
                    type=str, default="logging.yaml", help="日志配置文件名")

parser.add_argument('--api_config',
                    type=str, default="config.yaml", help="API配置文件名")

parser.add_argument('--update',
                    type=bool, default=True, help="客户列表是否有更新")

parser.add_argument('--clients',
                    type=str, default="clients.xlsx", help="客户列表文件名")

parser.add_argument('--targets',
                    type=str, default="targets.xlsx", help="洗钱机构列表文件名")
args = parser.parse_args()

if __name__ == '__main__':
    log_config = YamlReader(os.path.join(CONFIG_DIR, args.log_config)).read()
    logging.config.dictConfig(log_config)

    extractor = JiebaExtractor(get_corpnames_partial)

    api_config = YamlReader(os.path.join(CONFIG_DIR, args.api_config)).read()
    user_dicts = api_config.get('user_dicts', None)
    extractor.load_user_dicts(os.path.join(DATA_DIR, "user_dicts"), user_dicts)

    targets = get_corpnames_full(os.path.join(DATA_DIR, "raw", args.targets),
                                 "机构名称")
    extractor.extract(targets, os.path.join(DATA_DIR, "extracted", args.targets))

    if args.update:
        raw = get_corpnames_full(os.path.join(DATA_DIR, "raw", args.clients),
                                 "机构名称")
        extractor.extract(raw, os.path.join(DATA_DIR, "extracted", args.clients))


