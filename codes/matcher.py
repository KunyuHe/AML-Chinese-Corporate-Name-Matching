import logging
import os

import numpy as np
from dimsim import get_distance
from fuzzychinese import FuzzyChineseMatch
from joblib import dump, load

from codes import MODEL_DIR
from codes.util import arctan_mapping, text_sliding_window

logger = logging.getLogger(__name__)


class ChineseFuzzyMatcher:
    DEFAULT_WEIGHTS = {'phonetic': 0.3, 'stroke': 0.35, 'radical': 0.35}
    DEFAULT_THRESHOLD = 0.5

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

    def __init__(self, other, weights):
        self.__weights = ChineseFuzzyMatcher.check_weights(weights)

        self.__texts = None
        self.__other = other
        self.stroke_model = None
        self.radical_model = None

    @property
    def weights(self):
        return self.__weights

    @weights.setter
    def weights(self, value):
        self.__weights = ChineseFuzzyMatcher.check_weights(value)

    @property
    def texts(self):
        return self.__texts

    @property
    def other(self):
        return self.__other

    def load_self_texts(self, texts):
        self.__texts = texts

    def fit(self, ngram):
        if self.weights['stroke']:
            self.stroke_model = FuzzyChineseMatch(ngram_range=(ngram, ngram),
                                                  analyzer='stroke')
            self.stroke_model.fit(self.texts)
            logger.info("Stroke model updated.")
            dump(self.stroke_model, os.path.join(MODEL_DIR, 'stroke.joblib'))

        if self.weights['radical']:
            self.radical_model = FuzzyChineseMatch(ngram_range=(ngram, ngram),
                                                   analyzer='radical')
            self.radical_model.fit(self.texts)
            logger.info("Radical model updated.")
            dump(self.radical_model, os.path.join(MODEL_DIR, 'radical.joblib'))

    def load_models(self):
        path = os.path.join(MODEL_DIR, 'stroke.joblib')
        if os.path.isfile(path):
            self.stroke_model = load(path)
            logger.info("Stroke model loaded.")

        path = os.path.join(MODEL_DIR, 'radical.joblib')
        if os.path.isfile(path):
            self.radical_model = load(path)
            logger.info("Radical model loaded.")

    def evaluate(self):
        self.sim_matrix = np.zeros((len(self.other), len(self.texts)))

        if self.stroke_model:
            self.stroke_model.transform(self.other)
            self.sim_matrix += self.stroke_model.sim_matrix_ * \
                               self.weights['stroke']

        if self.radical_model:
            self.radical_model.transform(self.other)
            self.sim_matrix += self.radical_model.sim_matrix_ * \
                               self.weights['radical']

        if self.weights['phonetic']:
            for i, other_text in self.other.iteritems():
                for j, self_text in self.texts.iteritems():
                    sim = get_phonetic_similarity(other_text, self_text)
                    self.sim_matrix[i, j] += sim * self.weights['phonetic']

    def report(self, threshold):
        mask = np.any(self.sim_matrix >= threshold, axis=1)
        alert = self.sim_matrix[mask]

def get_phonetic_similarity(self, other):
    m, n = len(self), len(other)

    if m == n:
        return arctan_mapping(get_distance(self, other))

    if m < n:
        fixed, slide = self, other
    else:
        fixed, slide = other, self

    min_dist = min([get_distance(fixed, sub)
                    for sub in text_sliding_window(slide, min(m, n))])
    return arctan_mapping(min_dist)
