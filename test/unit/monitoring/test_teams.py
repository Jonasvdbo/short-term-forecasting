# SPDX-FileCopyrightText: 2017-2021 Alliander N.V. <korte.termijn.prognoses@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

from unittest.mock import MagicMock
from unittest.mock import patch

import pandas as pd

from stf.monitoring import teams

from test.utils import BaseTestCase, TestData


@patch("stf.monitoring.teams.pymsteams")
@patch("stf.monitoring.teams.ConfigManager", MagicMock())
class TestTeams(BaseTestCase):

    def setUp(self):
        self.pj = TestData.get_prediction_job(pid=307)

    def test_post_teams(self, teamsmock):

        msg = "test"

        teams.post_teams(msg)
        card_mock = teamsmock.connectorcard.return_value
        self.assertTrue(card_mock.send.called)


    def test_post_teams_alert(self, teamsmock):

        msg = "test"

        teams.post_teams_alert(msg)
        card_mock = teamsmock.connectorcard.return_value
        self.assertTrue(card_mock.send.called)


    def test_post_teams_better(self, teamsmock):

        test_feature_weights = pd.DataFrame(data={'gain': [1, 2]})

        teams.send_report_teams_better(self.pj, test_feature_weights)
        card_mock = teamsmock.connectorcard.return_value
        self.assertTrue(card_mock.send.called)

    @patch("stf.monitoring.teams.open", MagicMock())
    def test_post_teams_worse(self, teamsmock):

        teams.send_report_teams_worse(self.pj)
        card_mock = teamsmock.connectorcard.return_value
        self.assertTrue(card_mock.send.called)
