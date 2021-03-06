# SPDX-FileCopyrightText: 2017-2021 Alliander N.V. <korte.termijn.prognoses@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

from datetime import datetime, timedelta

from stf.model.capacity_prognosis import predict_capacity_prognosis
from stf.tasks.utils.predictionjobloop import PredictionJobLoop
from stf.tasks.utils.taskcontext import TaskContext


def main():
    with TaskContext("create_capacity_forecast") as context:
        # prediction horizons
        y_hor = list(range(13))

        # define input range
        datetime_start = datetime.utcnow().date() - timedelta(days=30)
        datetime_end = datetime.utcnow().date() + timedelta(days=max(y_hor) + 1)

        model_type = "xgb"
        PredictionJobLoop(
            context,
            model_type=model_type
        ).map(
            predict_capacity_prognosis,
            datetime_start=datetime_start,
            datetime_end=datetime_end,
            y_hor=y_hor,
        )


if __name__ == "__main__":
    main()
