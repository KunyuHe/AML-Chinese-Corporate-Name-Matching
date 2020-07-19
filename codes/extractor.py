import logging
import os

import jieba
import jieba.posseg as pseg
import numpy as np
import pandas as pd

from codes.util import create_dirs
from codes import DATA_DIR

logger = logging.getLogger(__name__)


def get_corpnames_partial(name):
    cut = list(pseg.cut(name))

    # 去掉开头的地名
    prefix = cut[0]
    if prefix.flag == 'ns':
        cut = cut[1:]

    res = ""
    for i, curr in enumerate(cut):
        # 如果括号中的内容为地名或者公司后缀，去掉括号中的内容
        if i > 0 and i < len(cut) - 1:
            if all([cut[i - 1].flag == 'x', cut[i + 1].flag == 'x',
                    curr.flag in ('ns', 'corp')]):
                continue

        # 去掉括号和公司后缀
        if cut[i].flag in ('x', 'corp'):
            continue
        res += cut[i].word

    if not res:
        res = prefix.word

    return res


class JiebaExtractor:
    def __init__(self, fn):
        jieba.initialize()
        self.fn = fn

        self.clients = None
        self.target = None

    @staticmethod
    def load_user_dicts(user_dicts=None):
        dir_path = os.path.join(DATA_DIR, "user_dicts")
        if not user_dicts:
            logger.info("No user defined dictionaries.")

        for user_dict in user_dicts:
            path = os.path.join(dir_path, user_dict)
            if not os.path.isfile(path):
                msg = f"User dictionary {user_dict} not found under {dir_path}."
                logger.error(msg)
                raise FileNotFoundError(msg)

            jieba.load_userdict(path)
            logger.info(f"User dictionary {user_dict} loaded.")

    def extract(self, data, filename, colname):
        extracted = pd.DataFrame(np.c_[data, data.apply(self.fn)],
                                 columns=[data.name, colname])

        dir_path = os.path.join(DATA_DIR, "extracted")
        create_dirs(dir_path)
        extracted.to_csv(os.path.join(dir_path, filename),
                         index=False, encoding='utf_8_sig')

        return extracted
