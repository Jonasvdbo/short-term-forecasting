# SPDX-FileCopyrightText: 2017-2021 Alliander N.V. <korte.termijn.prognoses@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

import unittest
from test.utils import BaseTestCase, TestData
from unittest import mock

from ktpbase.data_interface import _DataInterface
from ktpbase.services.splitting import Splitting
from ktpbase.services.weather import Weather

from stf.model import split_energy

# Get test data
input_data = TestData.load("find_components_input.csv")
components = TestData.load("find_components_components.csv")


class TestSplitEnergy(BaseTestCase):

    def test_find_components(self):
        testcomponents, coefdict = split_energy.find_components(input_data)
        self.assertDataframeEqual(components, testcomponents,  rtol=1E-3)


# Run all tests
if __name__ == "__main__":
    unittest.main()
