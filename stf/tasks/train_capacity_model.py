# SPDX-FileCopyrightText: 2017-2021 Alliander N.V. <korte.termijn.prognoses@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

from datetime import datetime

import pandas as pd

from stf.model.capacity_prognosis import train_capacity_prognosis
from stf.tasks.utils.predictionjobloop import PredictionJobLoop
from stf.tasks.utils.taskcontext import TaskContext

def main():
    with TaskContext("train_capacity_model") as context:
        # training horizons
        y_hor = [0, 6, 13]

        # define input range
        datetime_end = datetime.utcnow()
        datetime_start = datetime_end - pd.Timedelta("400D")

        model_type = "xgb"
        PredictionJobLoop(
            context,
            model_type=model_type
        ).map(
            train_capacity_prognosis,
            datetime_start=datetime_start,
            datetime_end=datetime_end,
            y_hor=y_hor,
        )

if __name__ == "__main__":
    main()

