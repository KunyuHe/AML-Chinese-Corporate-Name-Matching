import argparse
import logging.config
import pandas as pd
import os

from codes import CONFIG_DIR, DATA_DIR
from codes.extractor import JiebaExtractor, get_corpnames_partial
from codes.matcher import ChineseFuzzyMatcher
from codes.util import YamlReader, get_corpnames_full

parser = argparse.ArgumentParser()
parser.add_argument('--log_config',
                    type=str, default="logging.yaml", help="日志配置文件名")

parser.add_argument('--api_config',
                    type=str, default="config.yaml", help="API配置文件名")

parser.add_argument('--update',
                    type=bool, default=True, help="客户列表是否有更新")
args = parser.parse_args()


def read_raw(config):
    return get_corpnames_full(config['raw']['file'], config['raw']['col'])

def extract(extractor, data, config):
    return extractor.extract(data,
                             config['extracted']['file'],
                             config['extracted']['col'])


if __name__ == '__main__':
    log_config = YamlReader(os.path.join(CONFIG_DIR, args.log_config)).read()
    logging.config.dictConfig(log_config)

    api_config = YamlReader(os.path.join(CONFIG_DIR, args.api_config)).read()

    extractor = JiebaExtractor(fn=get_corpnames_partial)
    extractor.load_user_dicts(user_dicts=api_config['EXTRACTOR'].get('user_dicts',
                                                                     []))

    targets_config = api_config['TARGETS']
    targets = read_raw(targets_config)
    targets = extract(extractor, targets, targets_config)

    matcher_config = api_config["MATCHER"]
    matcher = ChineseFuzzyMatcher(
        weights=matcher_config.get('weights', {}),
        other=targets[targets_config['extracted']['col']]
    )

    clients_config = api_config["CLIENTS"]
    if args.update:
        clients = read_raw(clients_config)
        clients = extract(extractor, clients, clients_config)
    else:
        clients = pd.read_csv(os.path.join(DATA_DIR, "extracted",
                                           clients_config['extracted']['file']),
                              encoding='utf_8_sig')

    matcher.load_self_texts(clients[clients_config['extracted']['col']])
    if args.update:
        matcher.fit(ngram=matcher_config.get('ngram', 3))
    else:
        matcher.load_models()

    matcher.evaluate()
    matcher.report(matcher_config.get('threshold', 0.6))
