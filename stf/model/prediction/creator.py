# SPDX-FileCopyrightText: 2017-2021 Alliander N.V. <korte.termijn.prognoses@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

from stf.model.prediction.xgboost.quantile import QuantileXGBPredictionModel
from stf.model.prediction.xgboost.xgboost import XGBPredictionModel


class PredictionModelCreator:

    PROGNOSIS_MODEL_CONSTRUCTORS = {"xgb": XGBPredictionModel,
                                    "xgb_quantile": QuantileXGBPredictionModel}

    @classmethod
    def create_prediction_model(cls, pj, forecast_type, model=None, confidence_df=None):

        model_type = pj["model"]

        if model_type not in cls.PROGNOSIS_MODEL_CONSTRUCTORS:
            raise KeyError(f"Unknown model_type: '{model_type}'")

        return cls.PROGNOSIS_MODEL_CONSTRUCTORS[model_type](
            pj, forecast_type, model, confidence_df
        )
