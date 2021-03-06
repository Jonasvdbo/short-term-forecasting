# SPDX-FileCopyrightText: 2017-2021 Alliander N.V. <korte.termijn.prognoses@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

from datetime import datetime, timedelta
from test.utils.data import TestData
from unittest.mock import patch

import numpy as np
import pandas as pd

from stf.model.general import MLModelType, split_data_train_validation_test
from stf.model.serializer.creator import ModelSerializerCreator
from stf.model.serializer.xgboost.xgboost import XGBModelSerializer
from stf.model.train import is_data_sufficient
from stf.model.trainer.creator import ModelTrainerCreator
from stf.model.trainer.xgboost.xgboost import XGBModelTrainer

from test.utils import BaseTestCase

serializer_creator = ModelSerializerCreator()
serializer = serializer_creator.create_model_serializer(MLModelType("xgb"))

pj = TestData.get_prediction_job(pid=307)

datetime_start = datetime.utcnow() - timedelta(days=90)
datetime_end = datetime.utcnow()

data = pd.DataFrame(index=pd.date_range(datetime_start, datetime_end, freq="15T"))

data_table = TestData.load("input_data_train.pickle").head(8641)
# Fill dataframe with values for next test
data["load"] = np.arange(len(data))

params = {
    "subsample": 0.9,
    "min_child_weight": 4,
    "max_depth": 15,
    "gamma": 0.2,
    "colsample_bytree": 0.85,
    "silent": 1,
    "objective": "reg:linear",
}
confidence_interval_ref = TestData.load("confidence_interval.csv")

# Generate reference training input data
(
    training_data_ref,
    validation_data_ref,
    testing_data_ref,
) = split_data_train_validation_test(data_table)

# When True: generate a new reference model_trainer pickle:
if False:
    model_trainer_ref = XGBModelTrainer(pj)
    model_trainer_ref.hyper_parameters.update(params)
    model_trainer_ref.train(training_data_ref, validation_data_ref)
    TestData.save(model_trainer_ref, "model_trainer_reference.pickle")
else:
    # Get reference model_trainer object
    model_trainer_ref = TestData.load("model_trainer_reference.pickle")


class TestTrain(BaseTestCase):

    def setUp(self):
        self.data = data
        self.confidence_interval_ref = confidence_interval_ref

    def test_model_trainer_creator(self):
        model, model_file = serializer.load(123, TestData.TRAINED_MODELS_FOLDER)

        model_path = TestData.TRAINED_MODELS_FOLDER / "<pid>/20191119120000/model.bin"

        with patch.object(
            XGBModelSerializer, 'load', return_value=(model, model_path)
        ):
            model_trainer_creator = ModelTrainerCreator(pj)

            model_trainer = model_trainer_creator.create_model_trainer()

            self.assertEqual(type(model_trainer), XGBModelTrainer)

    def test_split_data_train_validation_test(self):
        train_data, validation_data, test_data = split_data_train_validation_test(
            self.data, period_sampling=False
        )
        self.assertEqual(len(train_data), 7345)
        self.assertEqual(len(validation_data), 1297)
        self.assertEqual(len(test_data), 1)

    def test_split_data_train_validation_test_period(self):
        train_data, validation_data, test_data = split_data_train_validation_test(
            self.data, period_sampling=True
        )
        self.assertEqual(len(train_data), 7345)
        self.assertEqual(len(validation_data), 1296)
        self.assertEqual(len(test_data), 1)

    def test_train_checks(self, data=data):
        # Happy flow
        sufficient = is_data_sufficient(data)
        self.assertTrue(sufficient)

        # Make 20% of data np.nan to simulate incompleteness that is still acceptable
        data.iloc[0: int(np.round(0.2 * len(data))), :] = np.nan
        sufficient = is_data_sufficient(data)
        self.assertTrue(sufficient)

        # Only pas first 50 rows
        sufficient = is_data_sufficient(data.iloc[0:50, :])
        self.assertFalse(sufficient)

        # Make 60% of data np.nan to simulate incompleteness that is not acceptable
        data.iloc[0: int(np.round(0.6 * len(data))), :] = np.nan
        sufficient = is_data_sufficient(data)
        self.assertFalse(sufficient)

    def test_xgboost_model_trainer_train_and_confidence_interval(self):
        # Train
        model = model_trainer_ref.train(training_data_ref, validation_data_ref)

        # verify a model has been trained
        self.assertTrue(hasattr(model, "predict"))

        # Calculate confidence interval
        confidence_interval = model_trainer_ref.calculate_confidence_interval(
            testing_data_ref)

        # Check if same as reference
        pd.testing.assert_index_equal(
            self.confidence_interval_ref.index,
            confidence_interval.index
        )


# Run all tests
if __name__ == "__main__":
    unittest.main()
