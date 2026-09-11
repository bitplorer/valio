# Copyright (c) 2022 Valio
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import unittest
from dataclasses import dataclass

from valio import PaymentCardValidator


class TestPaymentCardValidator(unittest.TestCase):
    """E13: brand match required; a Luhn-valid generator must not pass."""

    def setUp(self):
        @dataclass
        class Card(object):
            c: str = PaymentCardValidator(debug=True, logger=False)

        self.Card = Card

    def test_visa_test_number_is_accepted(self):
        self.assertEqual(self.Card(c="4111111111111111").c, "4111111111111111")

    def test_luhn_valid_non_brand_is_rejected(self):
        with self.assertRaises(ValueError):
            self.Card(c="0000000000000000")
        with self.assertRaises(ValueError):
            self.Card(c="79927398713")

    def test_luhn_invalid_is_rejected(self):
        with self.assertRaises(ValueError):
            self.Card(c="4111111111111112")
