import logging
import os
from collections import defaultdict

import numpy as np
from dimsim import get_distance
from fuzzychinese import FuzzyChineseMatch
from joblib import dump, load

from codes import MODEL_DIR, REPORT_DIR
from codes.util import arctan_mapping, text_sliding_window, view_df
import pandas as pd

logger = logging.getLogger(__name__)


class ChineseFuzzyMatcher:
    DEFAULT_WEIGHTS = {'phonetic': 0.3, 'stroke': 0.35, 'radical': 0.35}
    DEFAULT_THRESHOLD = 0.5
    DEFAULT_PENALTY = 0.1

    @classmethod
    def check_weights(cls, weights):
        for k, v in cls.DEFAULT_WEIGHTS.items():
            if k not in weights:
                logger.info(f"Weights for {k} not configured. Use default {v}.")
                weights[k] = v

        return weights

    @classmethod
    def check_threshold(cls, threshold):
        if not threshold:
            threshold = cls.DEFAULT_THRESHOLD
        return threshold

    @classmethod
    def check_penalty(cls, penalty):
        if not penalty:
            penalty = cls.DEFAULT_PENALTY
        return penalty

    def __init__(self, other, weights, penalty):
        self.__weights = ChineseFuzzyMatcher.check_weights(weights)
        self.__penalty = ChineseFuzzyMatcher.check_penalty(penalty)

        self.__texts = None
        self.__other = other
        self.model_dict = {}
        self.sim_dict = {}

    @property
    def weights(self):
        return self.__weights

    @property
    def penalty(self):
        return self.__penalty

    @property
    def texts(self):
        return self.__texts

    @property
    def other(self):
        return self.__other

    def load_self_texts(self, texts):
        self.__texts = texts

    def fit(self, ngram):
        for key in ('stroke', 'radical'):
            if not self.weights[key]:
                continue

            self.model_dict[key] = FuzzyChineseMatch(ngram_range=(ngram, ngram),
                                                     analyzer=key)
            self.model_dict[key].fit(self.texts)
            logger.info(f"{key.title()} model updated.")
            dump(self.model_dict[key], os.path.join(MODEL_DIR, f'{key}.joblib'))

    def load_models(self):
        for key in ('stroke', 'radical'):
            if not self.weights[key]:
                continue

            path = os.path.join(MODEL_DIR, f'{key}.joblib')
            if os.path.isfile(path):
                self.model_dict[key] = load(path)
                logger.info(f"{key.title()} model loaded.")

    def evaluate(self):
        self.sim_matrix = np.zeros((len(self.other), len(self.texts)))

        for key in ('stroke', 'radical'):
            if self.model_dict[key]:
                self.model_dict[key].transform(self.other)
                self.sim_dict[key] = self.model_dict[key].sim_matrix_
                self.sim_matrix += self.sim_dict[key] * self.weights[key]

        if self.weights['phonetic']:
            self.sim_dict['phonetic'] = np.array([
                [get_phonetic_similarity(other_text, self_text, self.penalty)
                 for self_text in self.texts]
                for other_text in self.other
            ])
            self.sim_matrix += self.sim_dict['phonetic'] * \
                               self.weights['phonetic']

    def report(self, threshold, texts, other, output_file):
        threshold = ChineseFuzzyMatcher.check_threshold(threshold)
        res = defaultdict(list)

        for i, target in other.iteritems():
            mask = (self.sim_matrix[i, :] >= threshold)
            if np.any(mask):
                n = len(self.sim_matrix[i, mask])
                res['目标'].extend([target] * n)
                res['目标简称'].extend([self.other[i]] * n)

                res['客户'].extend(texts[mask])
                res['客户简称'].extend(self.texts[mask])
                res[f'相似度（阈值 = {threshold}）'].extend(self.sim_matrix[i, mask])
                for header, key in zip(
                        ["音似（权重 = {}，长度错位惩罚项 = %s）" % self.penalty,
                         "形似（笔画，权重 = {}）", "形似（部首，权重 = {}）"],
                        ['phonetic', 'stroke', 'radical']
                ):
                    if not self.weights[key]:
                        res[header.format(self.weights[key])].extend([0] * n)
                    else:
                        res[header.format(self.weights[key])].extend(
                            self.sim_dict[key][i, mask]
                        )

        logger.info(res)
        res = pd.DataFrame(res).set_index(['目标', '客户'])
        res.to_csv(os.path.join(REPORT_DIR, output_file), encoding='utf_8_sig')
        view_df(res)


def get_phonetic_similarity(self, other, penalty):
    m, n = len(self), len(other)

    if m == n:
        return arctan_mapping(get_distance(self, other))

    if m < n:
        fixed, slide = self, other
    else:
        fixed, slide = other, self

    dists = [get_distance(fixed, sub)
             for sub in text_sliding_window(slide, min(m, n))]
    return arctan_mapping(min(dists) + penalty * len(dists))
