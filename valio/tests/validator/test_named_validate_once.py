# Copyright (c) 2022 Valio
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import unittest
from dataclasses import dataclass

from valio import HexColorValidator


class TestNamedValidateDoesNotRegisterItself(unittest.TestCase):
    """E15: named validate() must not append to _custom_validators."""

    def test_hex_color_validator_list_does_not_grow(self):
        v = HexColorValidator(debug=True, logger=False)

        @dataclass
        class H(object):
            h: str = v

        H(h="#fff")
        H(h="#ffffff")
        H(h="#abc")
        self.assertTrue(
            all(len(fns) <= 1 for fns in v._custom_validators.values()),
            v._custom_validators,
        )
        self.assertEqual(H(h="#fff").h, "#fff")
