# SPDX-FileCopyrightText: 2017-2021 Alliander N.V. <korte.termijn.prognoses@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

# import builtins
import unittest
from datetime import datetime
from unittest.mock import patch

import pandas as pd

# import project modules
from stf.model.capacity_prognosis import (
    predict_capacity_prognosis, train_capacity_prognosis
)

from test.utils import BaseTestCase, TestData

# define constants for mocking return values
FUCNTION_ARGS = [
    {"id": 1, "name": "job1", "description": "description for job 1"},
    datetime.utcnow().date(),
    datetime.utcnow().date(),
    list(range(13))
]
TIME_IND = pd.date_range(
    "2020-03-17 00:00:00+00:00", "2020-03-17 02:15:00+00:00", freq="15min"
)
LOAD_DATA = pd.DataFrame(
    [
        0.660000,
        1.163333,
        1.860000,
        1.826667,
        2.263333,
        2.516667,
        2.236667,
        2.280000,
        2.480000,
        1.960000,
    ],
    columns=["load"],
    index=TIME_IND,
)
SJV_DATA = pd.DataFrame(
    [
        [
            0.000023,
            0.000025,
            0.000025,
            0.000024,
            0.000025,
            0.000019,
            0.000021,
            0.000021,
            0.000025,
            6.024000e-05,
        ],
        [
            0.000022,
            0.000023,
            0.000023,
            0.000023,
            0.000024,
            0.000019,
            0.000021,
            0.000021,
            0.000025,
            6.024000e-05,
        ],
        [
            0.000021,
            0.000022,
            0.000022,
            0.000023,
            0.000024,
            0.000019,
            0.000020,
            0.000020,
            0.000025,
            6.024000e-05,
        ],
        [
            0.000020,
            0.000021,
            0.000021,
            0.000023,
            0.000024,
            0.000019,
            0.000020,
            0.000020,
            0.000026,
            6.024000e-05,
        ],
        [
            0.000019,
            0.000020,
            0.000020,
            0.000022,
            0.000023,
            0.000019,
            0.000020,
            0.000020,
            0.000026,
            6.024000e-05,
        ],
        [
            0.000019,
            0.000020,
            0.000020,
            0.000022,
            0.000023,
            0.000018,
            0.000020,
            0.000020,
            0.000025,
            6.024000e-05,
        ],
        [
            0.000018,
            0.000019,
            0.000019,
            0.000022,
            0.000023,
            0.000018,
            0.000020,
            0.000020,
            0.000026,
            6.024000e-05,
        ],
        [
            0.000017,
            0.000018,
            0.000019,
            0.000022,
            0.000023,
            0.000018,
            0.000020,
            0.000020,
            0.000026,
            6.024000e-05,
        ],
        [
            0.000017,
            0.000018,
            0.000019,
            0.000022,
            0.000023,
            0.000018,
            0.000020,
            0.000020,
            0.000026,
            6.024000e-05,
        ],
        [
            0.000017,
            0.000018,
            0.000018,
            0.000022,
            0.000023,
            0.000018,
            0.000020,
            0.000020,
            0.000026,
            6.024000e-05,
        ],
    ],
    columns=[
        "sjv_E1A",
        "sjv_E1B",
        "sjv_E1C",
        "sjv_E2A",
        "sjv_E2B",
        "sjv_E3A",
        "sjv_E3B",
        "sjv_E3C",
        "sjv_E3D",
        "sjv_E4A",
    ],
    index=TIME_IND,
)


@patch("stf.model.capacity_prognosis.visualize_predictions")
@patch("stf.model.capacity_prognosis.prepare_prediction_data")
@patch("stf.model.capacity_prognosis.CapacityPrognosisModel")
@patch("stf.model.capacity_prognosis.apply_capacity_features")
@patch("stf.model.capacity_prognosis.DataBase")
@patch("stf.model.capacity_prognosis.plotly")
class TestCapacityPrognosisPredict(BaseTestCase):
    def test_no_exception(
        self,
        plotly_mock,
        db_mock,
        apply_features_mock,
        model_mock,
        prepare_data_mock,
        visualize_predictions_mock,
    ):
        self.add_mock_return_values(
            plotly_mock,
            db_mock,
            apply_features_mock,
            model_mock,
            prepare_data_mock,
            visualize_predictions_mock,
        )

        # run function
        predict_capacity_prognosis(*FUCNTION_ARGS)

        # check mocks
        mocks_called = [
            db_mock.return_value.get_load_pid,
            db_mock.return_value.get_sjv,
            apply_features_mock,
            prepare_data_mock,
            model_mock,
            model_mock.return_value.predict,
            visualize_predictions_mock,
            plotly_mock.offline.plot,
        ]
        for mock in mocks_called:
            mock.assert_called_once()

    @staticmethod
    def add_mock_return_values(
        plotly_mock,
        db_mock,
        apply_features_mock,
        model_mock,
        prepare_data_mock,
        visualize_predictions_mock,
    ):
        # set database return values
        db_mock.return_value.get_load_pid.return_value = LOAD_DATA
        db_mock.return_value.get_sjv.return_value = SJV_DATA
        # set return values for function which return more then 1 argument
        apply_features_mock.return_value = "feature_data", "_"
        model_mock.return_value.predict.return_value = "y_pred", "y_pred_prob"


@patch("stf.model.capacity_prognosis.prepare_training_data")
@patch("stf.model.capacity_prognosis.CapacityPrognosisModel")
@patch("stf.model.capacity_prognosis.apply_capacity_features")
@patch("stf.model.capacity_prognosis.DataBase")
class TestCapacityPrognosisTrain(BaseTestCase):
    def test_no_exception(
        self,
        db_mock,
        apply_features_mock,
        model_mock,
        prepare_data_mock,
    ):
        self.add_mock_return_values(
            db_mock,
            apply_features_mock,
            model_mock,
            prepare_data_mock,
        )

        # run function
        train_capacity_prognosis(*FUCNTION_ARGS)

        # check mocks
        mocks_called = [
            db_mock.return_value.get_load_pid,
            db_mock.return_value.get_sjv,
            apply_features_mock,
            prepare_data_mock,
            model_mock,
            model_mock.return_value.train,
            model_mock.return_value.save,
        ]
        for mock in mocks_called:
            mock.assert_called_once()

    @staticmethod
    def add_mock_return_values(
        db_mock,
        apply_features_mock,
        model_mock,
        prepare_data_mock,

    ):
        # set database return values
        db_mock.return_value.get_load_pid.return_value = LOAD_DATA
        db_mock.return_value.get_sjv.return_value = SJV_DATA
        # set return values for function which return more then 1 argument
        apply_features_mock.return_value = "feature_data", "_"
        # model_mock.return_value.predict.return_value = "y_pred", "y_pred_prob"
        prepare_data_mock.return_value = (
            "train_x",
            "train_y",
            "train_h",
            "val_x",
            "val_y",
            "val_h",
        )


if __name__ == "__main__":
    unittest.main()
