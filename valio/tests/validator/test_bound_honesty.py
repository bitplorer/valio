# Copyright (c) 2022 Valio
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""Soft #8: 0 is a bound; gt/lt exclusive; remainder means multiple-of."""

import unittest

from valio.validator.validators import (
    LengthValidator,
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    MultipleValidator,
    ValueValidator,
)


class TestBoundHonestyZeroIsABound(unittest.TestCase):
    """Falsy 0 must not skip inclusive min/max/eq/length checks."""

    def test_min_value_zero_enforces_inclusive_floor(self):
        v = MinValueValidator(min_value=0, debug=True, logger=False)
        self.assertEqual(v.min_value, 0)
        v.validate(None, 0)
        v.validate(None, 1)
        with self.assertRaises(ValueError):
            v.validate(None, -1)

    def test_max_value_zero_enforces_inclusive_ceiling(self):
        v = MaxValueValidator(max_value=0, debug=True, logger=False)
        self.assertEqual(v.max_value, 0)
        v.validate(None, 0)
        v.validate(None, -1)
        with self.assertRaises(ValueError):
            v.validate(None, 1)

    def test_min_length_zero_is_a_bound_not_unset(self):
        v = MinLengthValidator(min_length=0, debug=True, logger=False)
        self.assertEqual(v.min_length, 0)
        v.validate(None, "")
        v.validate(None, "x")

    def test_max_length_zero_enforces(self):
        v = MaxLengthValidator(max_length=0, debug=True, logger=False)
        self.assertEqual(v.max_length, 0)
        v.validate(None, "")
        with self.assertRaises(ValueError):
            v.validate(None, "x")

    def test_length_zero_enforces_exact(self):
        v = LengthValidator(length=0, debug=True, logger=False)
        self.assertEqual(v.length, 0)
        v.validate(None, "")
        with self.assertRaises(ValueError):
            v.validate(None, "x")


class TestBoundHonestyExclusiveGtLt(unittest.TestCase):
    """gt/lt are exclusive; min_value/max_value stay inclusive."""

    def test_gt_zero_rejects_zero_accepts_one(self):
        v = MinValueValidator(gt=0, debug=True, logger=False)
        with self.assertRaises(ValueError):
            v.validate(None, 0)
        v.validate(None, 1)

    def test_lt_zero_rejects_zero_accepts_minus_one(self):
        v = MaxValueValidator(lt=0, debug=True, logger=False)
        with self.assertRaises(ValueError):
            v.validate(None, 0)
        v.validate(None, -1)

    def test_value_validator_gt_lt_exclusive(self):
        gt = ValueValidator(gt=0, debug=True, logger=False)
        with self.assertRaises(ValueError):
            gt.validate(None, 0)
        gt.validate(None, 1)

        lt = ValueValidator(lt=0, debug=True, logger=False)
        with self.assertRaises(ValueError):
            lt.validate(None, 0)
        lt.validate(None, -1)

    def test_min_value_zero_with_gt_none_does_not_collapse(self):
        v = MinValueValidator(min_value=0, gt=None, debug=True, logger=False)
        self.assertEqual(v.min_value, 0)
        v.validate(None, 0)
        with self.assertRaises(ValueError):
            v.validate(None, -1)

    def test_max_value_zero_with_lt_none_does_not_collapse(self):
        v = MaxValueValidator(max_value=0, lt=None, debug=True, logger=False)
        self.assertEqual(v.max_value, 0)
        v.validate(None, 0)
        with self.assertRaises(ValueError):
            v.validate(None, 1)

    def test_value_validator_min_value_zero_gt_none_does_not_collapse(self):
        v = ValueValidator(min_value=0, gt=None, debug=True, logger=False)
        self.assertEqual(v.min_value, 0)
        v.validate(None, 0)
        with self.assertRaises(ValueError):
            v.validate(None, -1)


class TestBoundHonestyEqValueZero(unittest.TestCase):
    """eq/value=0 is kept and enforced."""

    def test_value_zero_is_kept_and_enforced(self):
        v = ValueValidator(value=0, debug=True, logger=False)
        self.assertEqual(v.value, 0)
        v.validate(None, 0)
        with self.assertRaises(ValueError):
            v.validate(None, 1)

    def test_eq_zero_is_kept_and_enforced(self):
        v = ValueValidator(eq=0, debug=True, logger=False)
        self.assertEqual(v.value, 0)
        v.validate(None, 0)
        with self.assertRaises(ValueError):
            v.validate(None, 1)


class TestBoundHonestyMultipleOf(unittest.TestCase):
    """Remainder means multiple-of; multiple_of=0 is a bound, not unset."""

    def test_multiple_of_two_accepts_multiples_rejects_remainder(self):
        v = MultipleValidator(multiple_of=2, debug=True, logger=False)
        v.validate(None, 0)
        v.validate(None, 2)
        v.validate(None, 4)
        with self.assertRaises(ValueError):
            v.validate(None, 1)
        with self.assertRaises(ValueError):
            v.validate(None, 3)

    def test_multiple_of_zero_is_kept_and_safe(self):
        v = MultipleValidator(multiple_of=0, debug=True, logger=False)
        self.assertEqual(v.multiple_of, 0)
        v.validate(None, 0)
        with self.assertRaises(ValueError):
            v.validate(None, 1)


if __name__ == "__main__":
    unittest.main()
