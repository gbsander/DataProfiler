# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://github.com/tensorflow/addons/blob/v0.12.0/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

# Adapt the test from https://github.com/tensorflow/addons/blob/v0.12.0/tensorflow_addons/metrics/tests/f_scores_test.py
"""Tests F beta metrics."""

import unittest

import numpy as np
import tensorflow as tf

from dataprofiler.labelers.character_level_cnn_model import F1Score, FBetaScore


class TestFScore(unittest.TestCase):

    def test_config_fbeta(self):
        fbeta_obj = FBetaScore(num_classes=3, beta=0.5, threshold=0.3, average=None)
        assert fbeta_obj.beta == 0.5
        assert fbeta_obj.average is None
        assert fbeta_obj.threshold == 0.3
        assert fbeta_obj.num_classes == 3
        assert fbeta_obj.dtype == tf.float32

        # Check save and restore config
        fbeta_obj2 = FBetaScore.from_config(fbeta_obj.get_config())
        assert fbeta_obj2.beta == 0.5
        assert fbeta_obj2.average is None
        assert fbeta_obj2.threshold == 0.3
        assert fbeta_obj2.num_classes == 3
        assert fbeta_obj2.dtype == tf.float32

    def _test_tf(self, avg, beta, act, pred, sample_weights, threshold):
        act = tf.constant(act, tf.float32)
        pred = tf.constant(pred, tf.float32)

        fbeta = FBetaScore(3, avg, beta, threshold)
        fbeta.update_state(act, pred, sample_weights)
        return fbeta.result().numpy()

    def _test_fbeta_score(self, actuals, preds, sample_weights, avg, beta_val, result, threshold):
        tf_score = self._test_tf(avg, beta_val, actuals, preds, sample_weights, threshold)
        np.testing.assert_allclose(tf_score, result, atol=1e-7, rtol=1e-6)

    def test_fbeta_perfect_score(self):
        preds = [[0.7, 0.7, 0.7], [1, 0, 0], [0.9, 0.8, 0]]
        actuals = [[1, 1, 1], [1, 0, 0], [1, 1, 0]]

        for avg_val in ["micro", "macro", "weighted"]:
            for beta in [0.5, 1.0, 2.0]:
                self._test_fbeta_score(actuals, preds, None, avg_val, beta, 1.0, 0.66)

    def test_fbeta_worst_score(self):
        preds = [[0.7, 0.7, 0.7], [1, 0, 0], [0.9, 0.8, 0]]
        actuals = [[0, 0, 0], [0, 1, 0], [0, 0, 1]]

        for avg_val in ["micro", "macro", "weighted"]:
            for beta in [0.5, 1.0, 2.0]:
                self._test_fbeta_score(actuals, preds, None, avg_val, beta, 0.0, 0.66)

    def test_fbeta_random_score(self):
        # Modification: bring parameters inside the tests
        params = [
            (None, 0.5, [0.71428573, 0.5, 0.833334]),
            (None, 1.0, [0.8, 0.5, 0.6666667]),
            (None, 2.0, [0.9090904, 0.5, 0.555556]),
            ("micro", 0.5, 0.6666667),
            ("micro", 1.0, 0.6666667),
            ("micro", 2.0, 0.6666667),
            ("macro", 0.5, 0.6825397),
            ("macro", 1.0, 0.6555555),
            ("macro", 2.0, 0.6548822),
            ("weighted", 0.5, 0.6825397),
            ("weighted", 1.0, 0.6555555),
            ("weighted", 2.0, 0.6548822),
        ]

        preds = [[0.7, 0.7, 0.7], [1, 0, 0], [0.9, 0.8, 0]]
        actuals = [[0, 0, 1], [1, 1, 0], [1, 1, 1]]

        for avg_val, beta, result in params:
            self._test_fbeta_score(actuals, preds, None, avg_val, beta, result, 0.66)

    def test_fbeta_random_score_none(self):
        # Modification: bring parameters inside the tests
        params = [
            (None, 0.5, [0.9090904, 0.555556, 1.0]),
            (None, 1.0, [0.8, 0.6666667, 1.0]),
            (None, 2.0, [0.71428573, 0.833334, 1.0]),
            ("micro", 0.5, 0.833334),
            ("micro", 1.0, 0.833334),
            ("micro", 2.0, 0.833334),
            ("macro", 0.5, 0.821549),
            ("macro", 1.0, 0.822222),
            ("macro", 2.0, 0.849206),
            ("weighted", 0.5, 0.880471),
            ("weighted", 1.0, 0.844445),
            ("weighted", 2.0, 0.829365),
        ]
        preds = [
            [0.9, 0.1, 0],
            [0.2, 0.6, 0.2],
            [0, 0, 1],
            [0.4, 0.3, 0.3],
            [0, 0.9, 0.1],
            [0, 0, 1],
        ]
        actuals = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0], [1, 0, 0], [0, 0, 1]]

        for avg_val, beta, result in params:
            self._test_fbeta_score(actuals, preds, None, avg_val, beta, result, None)

    def test_fbeta_weighted_random_score_none(self):
        # Modification: bring parameters inside the tests
        params = [
            (None, 0.5, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], [0.909091, 0.555556, 1.0]),
            (None, 0.5, [1.0, 0.0, 1.0, 1.0, 0.0, 1.0], [1.0, 0.0, 1.0]),
            (None, 0.5, [0.5, 1.0, 1.0, 1.0, 0.5, 1.0], [0.9375, 0.714286, 1.0]),
            (None, 1.0, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], [0.8, 0.666667, 1.0]),
            (None, 1.0, [1.0, 0.0, 1.0, 1.0, 0.0, 1.0], [1.0, 0.0, 1.0]),
            (None, 1.0, [0.5, 1.0, 1.0, 1.0, 0.5, 1.0], [0.857143, 0.8, 1.0]),
            (None, 2.0, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], [0.714286, 0.833333, 1.0]),
            (None, 2.0, [1.0, 0.0, 1.0, 1.0, 0.0, 1.0], [1.0, 0.0, 1.0]),
            (None, 2.0, [0.5, 1.0, 1.0, 1.0, 0.5, 1.0], [0.789474, 0.909091, 1.0]),
            ("micro", 0.5, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 0.833333),
            ("micro", 0.5, [1.0, 0.0, 1.0, 1.0, 0.0, 1.0], 1.0),
            ("micro", 0.5, [0.5, 1.0, 1.0, 1.0, 0.5, 1.0], 0.9),
            ("micro", 1.0, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 0.833333),
            ("micro", 1.0, [1.0, 0.0, 1.0, 1.0, 0.0, 1.0], 1.0),
            ("micro", 1.0, [0.5, 1.0, 1.0, 1.0, 0.5, 1.0], 0.9),
            ("micro", 2.0, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 0.833333),
            ("micro", 2.0, [1.0, 0.0, 1.0, 1.0, 0.0, 1.0], 1.0),
            ("micro", 2.0, [0.5, 1.0, 1.0, 1.0, 0.5, 1.0], 0.9),
            ("macro", 0.5, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 0.821549),
            ("macro", 0.5, [1.0, 0.0, 1.0, 1.0, 0.0, 1.0], 0.666667),
            ("macro", 0.5, [0.5, 1.0, 1.0, 1.0, 0.5, 1.0], 0.883929),
            ("macro", 1.0, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 0.822222),
            ("macro", 1.0, [1.0, 0.0, 1.0, 1.0, 0.0, 1.0], 0.666667),
            ("macro", 1.0, [0.5, 1.0, 1.0, 1.0, 0.5, 1.0], 0.885714),
            ("macro", 2.0, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 0.849206),
            ("macro", 2.0, [1.0, 0.0, 1.0, 1.0, 0.0, 1.0], 0.666667),
            ("macro", 2.0, [0.5, 1.0, 1.0, 1.0, 0.5, 1.0], 0.899522),
            ("weighted", 0.5, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 0.880471),
            ("weighted", 0.5, [1.0, 0.0, 1.0, 1.0, 0.0, 1.0], 1.0),
            ("weighted", 0.5, [0.5, 1.0, 1.0, 1.0, 0.5, 1.0], 0.917857),
            ("weighted", 1.0, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 0.844444),
            ("weighted", 1.0, [1.0, 0.0, 1.0, 1.0, 0.0, 1.0], 1.0),
            ("weighted", 1.0, [0.5, 1.0, 1.0, 1.0, 0.5, 1.0], 0.902857),
            ("weighted", 2.0, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 0.829365),
            ("weighted", 2.0, [1.0, 0.0, 1.0, 1.0, 0.0, 1.0], 1.0),
            ("weighted", 2.0, [0.5, 1.0, 1.0, 1.0, 0.5, 1.0], 0.897608),
        ]

        preds = [
            [0.9, 0.1, 0],
            [0.2, 0.6, 0.2],
            [0, 0, 1],
            [0.4, 0.3, 0.3],
            [0, 0.9, 0.1],
            [0, 0, 1],
        ]
        actuals = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0], [1, 0, 0], [0, 0, 1]]

        for avg_val, beta, sample_weights, result in params:
            self._test_fbeta_score(actuals, preds, sample_weights, avg_val, beta, result, None)

    def test_eq(self):
        f1 = F1Score(3)
        fbeta = FBetaScore(3, beta=1.0)

        preds = [
            [0.9, 0.1, 0],
            [0.2, 0.6, 0.2],
            [0, 0, 1],
            [0.4, 0.3, 0.3],
            [0, 0.9, 0.1],
            [0, 0, 1],
        ]
        actuals = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0], [1, 0, 0], [0, 0, 1]]

        fbeta.update_state(actuals, preds)
        f1.update_state(actuals, preds)
        np.testing.assert_allclose(fbeta.result().numpy(), f1.result().numpy())

    def test_sample_eq(self):
        f1 = F1Score(3)
        f1_weighted = F1Score(3)

        preds = [
            [0.9, 0.1, 0],
            [0.2, 0.6, 0.2],
            [0, 0, 1],
            [0.4, 0.3, 0.3],
            [0, 0.9, 0.1],
            [0, 0, 1],
        ]
        actuals = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 0, 0], [1, 0, 0], [0, 0, 1]]
        sample_weights = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        f1.update_state(actuals, preds)
        f1_weighted(actuals, preds, sample_weights)
        np.testing.assert_allclose(f1.result().numpy(), f1_weighted.result().numpy())


if __name__ == '__main__':
    unittest.main()
