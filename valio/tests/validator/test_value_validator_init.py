# Copyright (c) 2022 Valio
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import unittest
from decimal import Decimal

from valio.validator.validators import DecimalValidator, ValueValidator


class TestValueValidatorInit(unittest.TestCase):
    """E16: one-sided bounds must not TypeError; 0 is a real bound."""

    def test_one_sided_value_does_not_typeerror(self):
        ValueValidator(value=1, debug=True, logger=False)
        DecimalValidator(debug=True, logger=False, value=Decimal("1"))

    def test_zero_eq_is_kept(self):
        v = ValueValidator(value=0, max_value=10, debug=True, logger=False)
        self.assertEqual(v.value, 0)

    def test_value_above_max_still_raises(self):
        with self.assertRaises(ValueError):
            ValueValidator(value=11, max_value=10, debug=True, logger=False)
