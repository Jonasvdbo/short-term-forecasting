# SPDX-FileCopyrightText: 2017-2021 Alliander N.V. <korte.termijn.prognoses@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np
import pandas as pd


def apply_resample(df, to_resample, timedelta):
    """
    This functions return a new resampled dataframe with timedelta resolution

    Args:
        df (pandas.DataFrame): pandas TimeSeries DataFrame
        to_resample (dict): Dictionary that indicates what columns to resample and how.
            Example: {'column': ['mean'], ['sum']}
        timedelta (str): Resolution to resample to ('H', 'D', 'M', etc)
    Return:
        pandas.DataFrame:
    """

    # Resampled dataframe
    r_df = pd.DataFrame()

    # Resample data for each column
    for column in to_resample:
        for op in to_resample[column]:
            r_df[column + "_" + op] = df[column].resample(timedelta).agg(op)

    return r_df


def apply_calender_features(df):
    # compute calender features
    df["is_monday"] = df.index.weekday == 0
    df["is_tuesday"] = df.index.weekday == 1
    df["is_wednesday"] = df.index.weekday == 2
    df["is_thurday"] = df.index.weekday == 3
    df["is_friday"] = df.index.weekday == 4
    df["is_saturday"] = df.index.weekday == 5
    df["is_sunday"] = df.index.weekday == 6
    df["is_weekday"] = df.index.weekday < 5
    df["is_weekendday"] = (df.index.weekday // 5) == 1
    df["month"] = df.index.month
    df["quarter"] = df.index.quarter

    return df


def apply_lag_features(df, lag_features, lag_times):
    lags = {}
    for t in lag_times:
        lags[t] = []
        for lag_feature in lag_features:
            # lag feature name
            name = lag_feature + "-" + str(t)
            # compute lag
            df[name] = df[lag_feature].shift(t)
            # ...
            lags[t].append(name)

    return df, lags


def apply_horizons(df, y_hor, lags, resample=False):
    # new dataframes
    dfs = []

    # copy of original dataframe
    df_copy = df.copy()

    for h in y_hor:
        # make copy of dataframe copy
        df_copy = df_copy.copy()

        # insert new column with horizon name
        df_copy["horizon"] = str(h)

        # alter copy
        for t in sorted(list(lags.keys())):
            # if horizon beyond lag variable
            if h >= t:
                # 'forget' lag features at time t
                for lag_feature in lags[t]:
                    df_copy[lag_feature] = np.nan

        # save copy
        dfs.append(df_copy)

    # concat dataframes
    df = pd.concat(dfs)

    if resample:
        # resample back to its original size
        # so that for each datapoint, one horizon variant exists
        i = np.array(range(len(df))).reshape(len(y_hor), -1).T
        c = np.random.choice(range(len(y_hor)), len(i), p=[0.8, 0.1, 0.1])
        i = i[range(len(i)), c]
        df = df.iloc[i]

    return df


def apply_outlier_removal(df, col):
    # compute high and low quantiles
    high_q = df[col].quantile(0.99)
    low_q = df[col].quantile(0.01)

    # remove outliers
    df = df[df[col] < high_q]
    df = df[df[col] > low_q]

    return df


def compute_classes(df):
    # compute quantiles
    quantiles = df.quantile([0.5, 0.75, 0.9]).values.flatten()

    # define class boundaries
    bounds = [0] + list(quantiles) + [df.max() + 0.1]

    # define classes
    classes = {}
    for i in range(len(bounds) - 1):
        classes[chr(65 + i)] = (bounds[i], bounds[i + 1])

    return classes


def apply_classes(df, y_col, classes):
    # convert y_col values to class labels
    y = df.copy()[y_col]
    for c in classes:
        lower, upper = classes[c]
        y[(df[y_col] >= lower) & (df[y_col] < upper)] = c

    # update original dataframe
    df[y_col] = y

    # TODO make this more general

    # Only use strings
    df = df.loc[df[y_col].apply(lambda x: isinstance(x, (str)) or np.isnan(x))]

    return df


def apply_capacity_features(
    df, y_col, y_hor, apply_class_labels=True, outlier_removal=False
):
    # apply resample
    to_resample = {
        "load": ["mean", "min", "max"],
        "sjv_E1A": ["max"],
        "sjv_E1B": ["max"],
        "sjv_E1C": ["max"],
        "sjv_E2A": ["max"],
        "sjv_E2B": ["max"],
        "sjv_E3A": ["max"],
        "sjv_E3B": ["max"],
        "sjv_E3C": ["max"],
    }
    df = apply_resample(df, to_resample=to_resample, timedelta="D")

    # remove outliers
    if outlier_removal:
        df = apply_outlier_removal(df, col=y_col)

    # apply lag features
    lag_features = df.columns
    lag_times = list(range(1, 28))
    df, lags = apply_lag_features(df, lag_features, lag_times)

    # apply horizons (size of new data frame is: samples * horizons)
    df = apply_horizons(df, y_hor, lags, resample=False)

    # apply calender features
    df = apply_calender_features(df)

    # apply classes
    classes = None
    if apply_class_labels:
        classes = compute_classes(df[y_col])
        df = apply_classes(df, y_col=y_col, classes=classes)

    # drop lag features
    df = df.drop(columns=[f for f in lag_features if f != y_col])

    # sort index
    df = df.sort_index()

    return df, classes
