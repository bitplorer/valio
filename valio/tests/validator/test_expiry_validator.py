# Copyright (c) 2022 Valio
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import unittest

from valio.validator.validators import ExpiryValidator


class TestExpiryValidatorInit(unittest.TestCase):
    """E18: expire_before is its own bound, not expire_after."""

    def test_expire_before_string_sets_timeline(self):
        e = ExpiryValidator(expire_before="2020-01-01", debug=True)
        self.assertEqual(e.timeline, "before")
        self.assertEqual(e.expiry, "2020-01-01")

    def test_expire_before_bad_string_is_rejected(self):
        with self.assertRaises(ValueError):
            ExpiryValidator(expire_before="not-a-date", debug=True)

    def test_expire_after_only_still_sets_timeline(self):
        e = ExpiryValidator(expire_after="2020-01-01", debug=True)
        self.assertEqual(e.timeline, "after")
