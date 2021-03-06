# SPDX-FileCopyrightText: 2017-2021 Alliander N.V. <korte.termijn.prognoses@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path

import pymsteams
from ktpbase.config.config import ConfigManager


def post_teams(msg, url=None):
    """Post a message to Teams - KTP

    Note that currently no authentication occurs.
    Security is given by keeping the URL secret.
    One should therefore refrain from using more enhanced features such as
    action buttons.

    Args:
        msg (mixed): For simple messages a string can be passed. For more
            complex messages pass a dict. The following keys are supported:
            text, links, sections. Each section can contain the following keys:
            text, title, images, facts, markdown. Also see:
            https://docs.microsoft.com/en-us/outlook/actionable-messages/send-via-connectors
        url (string, optional): webhook url, monitoring by default

    Returns:
        connectorcard: The card created and send to the teams channel

    Note:
        This function is namespace-specific.

    """
    config = ConfigManager.get_instance()

    if url is None:
        url = config.teams.monitoring_url

    card = pymsteams.connectorcard(url)

    # add proxies
    # NOTE the connectorcard.proxy is passed to the requests library under the hood
    card.proxies = config.proxies

    # if msg is string, convert to dict
    if type(msg) is str:
        msg = dict(text=msg)
    card.text(msg.get("text"))
    card.summary(msg.get("fallback", "-"))

    # set title, color, ...
    card.color(msg.get("color", "white"))
    card.title(msg.get("title"))

    for link_dict in msg.get("links", []):
        card.addLinkButton(link_dict["buttontext"], link_dict["buttonurl"])

    # Add sections
    for section_dict in msg.get("sections", []):
        section = pymsteams.cardsection()

        section.text(section_dict.get("text"))
        section.title(section_dict.get("title"))
        for image in section_dict.get("images", []):
            section.addImage(image)
        for fact in section_dict.get("facts", []):
            section.addFact(*fact)
        if not section_dict.get("markdown", True):
            section.disableMarkdown()
        if "link" in section_dict:
            section.linkButton(
                section_dict.get("link").get("buttontext"),
                section_dict.get("link").get("buttonurl"),
            )

        card.addSection(section)

    card.send()
    return card


def post_teams_alert(msg, url=None):
    """Same as post_teams, but posts to alert channel.

    Args:
    msg (mixed): For simple messages a string can be passed. For more
            complex messages pass a dict. The following keys are supported:
            text, links, sections. Each section is a dict and can contain the
            following keys: text, title, images, facts, markdown. Also see:
            https://docs.microsoft.com/en-us/outlook/actionable-messages/send-via-connectors

    Returns:
        connectorcard: The card created and send to the teams channel.

    Note:
        This function is namespace-specific.

    """
    if url is None:
        url = ConfigManager.get_instance().teams.alert_url

    return post_teams(msg, url=url)


def send_report_teams_better(pj, feature_importance):
    """Send a report to teams for monitoring input for an improved model.

    Post includes information (performance, figures, etc.) about the trained
    model. Use when the new trained model is better than the old model.

    Args:
        pj (dict): A dictionarry specifying the prediction job. This dict should
            at least contain the following keys: {
                'id': (int),
                'sid': (str),
                'name': (str),
                'horizon_minutes': (int),
                'resolution_minutes': (int),
                'lat': (float),
                'lon': (float),
                'description': (str)
            }.
            Usually this dictionary results from querrying the 'predictions'
            table in the SQL database.
        feature_importance (pandas.DataFrame): A DataFrame describing the
            feature importances and weights of the trained model.
    model: XGBoost model object of the newly trained model

    Returns:
        None

    """
    config = ConfigManager.get_instance()
    web_link = f'{config.dashboard.trained_models_url}/{pj["id"]}'

    msg = {
        "fallback": f'Trained better model: {pj["name"]}',
        "title": "Trained better model",
        "sections": [
            {
                "facts": [
                    ("Name", pj["name"]),
                    ("Desc", pj["description"]),
                    ("pid", pj["id"]),
                ],
                "markdown": False
            },
            {
                "title": "Dominant features",
                "facts": [
                    (
                        feature_importance.index[0],
                        f'{feature_importance["gain"][0]:.1%}'
                    ),
                    (
                        feature_importance.index[1],
                        f'{feature_importance["gain"][1]:.1%}'
                    ),
                ]
            }
        ],
        "links": [
            {
                "buttontext": "Train Performance",
                "buttonurl": f"{web_link}/Predictor47.0.html",
            },
            {
                "buttontext": "Model Weights",
                "buttonurl": f"{web_link}/weight_plot.html"
            },
        ],
        "color": "#764FA5",
    }

    post_teams(msg)


def send_report_teams_worse(pj):
    """Send a report to teams for monitoring input for a worsened model.

    Post includes information (performance, figures, etc.) about the trained
    model. Use when the new trained model is worse than the old model.

    Args:
        pj (dict): A dictionarry specifying the prediction job. This dict should
            at least contain the following keys: {
                'id': (int),
                'sid': (str),
                'name': (str),
                'horizon_minutes': (int),
                'resolution_minutes': (int),
                'lat': (float),
                'lon': (float),
                'description': (str)
            }.
            Usually this dictionary results from querrying the 'predictions'
            table in the SQL database.
    model: XGBoost model object of the newly trained model

    Returns:
        None

    """
    config = ConfigManager.get_instance()
    web_link_old = f'{config.dashboard.trained_models_url}/{pj["id"]}'
    web_link_new = f'{config.dashboard.trained_models_url}/{pj["id"]}/worse_model'

    image_save_location = Path(config.paths.trained_models) / f'{pj["id"]}'

    with open(image_save_location / "worse_model" / "Predictor47.0.datauri", "rt") as f:
        graph = f.read()

    msg = {
        "fallback": f'Trained worse model: {pj["name"]}',
        "title": "Warning",
        "text": "Old model is better. Please check and retrain using tracy if necessary.",
        "sections": [
            {
                "facts": [
                    ("Name", pj["name"]),
                    ("Desc", pj["description"]),
                    ("pid", pj["id"]),
                ],
                "markdown": False
            },
            {
                "title": "New Model Performance",
                "images": [
                    graph
                ],
            },
        ],
        "links": [
            {
                "buttontext": "Old Model Performance",
                "buttonurl": f"{web_link_old}/Predictor47.0.html",
            },
            {
                "buttontext": "New Model Performance",
                "buttonurl": f"{web_link_new}/Predictor47.0.html",
            },
            {
                "buttontext": "Old Model Weights",
                "buttonurl": f"{web_link_old}/weight_plot.html"
            },
            {
                "buttontext": "New Model Weights",
                "buttonurl": f"{web_link_new}/weight_plot.html",
            },
        ],
        "color": "#a5764f",
    }

    post_teams(msg)
