# SPDX-FileCopyrightText: 2017-2021 Alliander N.V. <korte.termijn.prognoses@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

# -*- coding: utf-8 -*-
"""create_basecase_forecast.py

This module should be executed once every day. For all prediction_jobs, it will
create a 'basecase' forecast which is less accurate, but (almost) always available.
For now, it uses the load a week earlier.
Missing datapoints are interpolated.

Example:
    This module is meant to be called directly from a CRON job. A description of the
    CRON job can be found in the /k8s/CronJobs folder.

    Alternatively this code can be run directly by running:

        $ python create_basecase_forecast.py
"""
import stf.model.predict as predict
from stf.tasks.utils.predictionjobloop import PredictionJobLoop
from stf.tasks.utils.taskcontext import TaskContext


def main():
    with TaskContext("create_basecase_forecast") as context:
        model_type = "xgb"

        PredictionJobLoop(
            context,
            model_type=model_type
        ).map(predict.make_basecase_prediction)


if __name__ == "__main__":
    main()
