# Copyright (c) 2022 Valio
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""Soft #9: readable None-only exclusion; Value/Length compose leaf bounds."""

import ast
import inspect
import pathlib
import unittest
from dataclasses import dataclass

from valio.validator import validators as validators_mod
from valio.validator.validators import (
    IntegerValidator,
    LengthValidator,
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    MultipleValidator,
    StringValidator,
    ValidateProperty,
    Validator,
    ValueValidator,
)


VALIDATORS_PATH = pathlib.Path(validators_mod.__file__)


class TestSoft9AllSpecifiedHonesty(unittest.TestCase):
    """all(... is not None) treats 0 as present; None as unset."""

    def test_zero_is_specified_none_is_not(self):
        self.assertTrue(hasattr(validators_mod, "_all_specified"))
        all_specified = validators_mod._all_specified
        self.assertTrue(all_specified(0, 0))
        self.assertTrue(all_specified(0))
        self.assertFalse(all_specified(0, None))
        self.assertFalse(all_specified(None, 0))
        self.assertFalse(all_specified(None, None))

    def test_helper_is_none_only_not_truthy(self):
        self.assertTrue(hasattr(validators_mod, "_all_specified"))
        src = inspect.getsource(validators_mod._all_specified)
        self.assertIn("all(bound is not None for bound in bounds)", src)
        self.assertNotIn("all([", src)
        self.assertNotIn("if bound", src)


class TestSoft9ValueLengthComposeNotInherit(unittest.TestCase):
    """Facades compose leaf min/max; they do not dual-inherit them."""

    def test_value_validator_is_not_min_or_max_subclass(self):
        self.assertFalse(issubclass(ValueValidator, MinValueValidator))
        self.assertFalse(issubclass(ValueValidator, MaxValueValidator))
        self.assertTrue(issubclass(ValueValidator, ValidateProperty))

    def test_length_validator_is_not_min_or_max_subclass(self):
        self.assertFalse(issubclass(LengthValidator, MinLengthValidator))
        self.assertFalse(issubclass(LengthValidator, MaxLengthValidator))
        self.assertTrue(issubclass(LengthValidator, ValidateProperty))

    def test_validator_facade_does_not_inherit_leaf_bounds(self):
        self.assertFalse(issubclass(Validator, MinValueValidator))
        self.assertFalse(issubclass(Validator, MaxValueValidator))
        self.assertFalse(issubclass(Validator, MinLengthValidator))
        self.assertFalse(issubclass(Validator, MaxLengthValidator))
        # Soft #10 deepen: Validator composes Value/Length too (does not inherit).
        self.assertFalse(issubclass(Validator, ValueValidator))
        self.assertFalse(issubclass(Validator, LengthValidator))
        self.assertTrue(issubclass(Validator, ValidateProperty))


class TestSoft9PublicUsageKeep(unittest.TestCase):
    """Public constructors, attributes, and happy-path assignment KEEP."""

    def test_value_validator_ctor_and_attributes(self):
        v = ValueValidator(min_value=0, max_value=10, debug=True, logger=False)
        self.assertEqual(v.min_value, 0)
        self.assertEqual(v.max_value, 10)
        self.assertIsNone(v.gt)
        self.assertIsNone(v.lt)
        self.assertIsNone(v.value)
        v.validate(None, 0)
        v.validate(None, 10)
        with self.assertRaises(ValueError):
            v.validate(None, -1)
        with self.assertRaises(ValueError):
            v.validate(None, 11)

    def test_length_validator_ctor_and_attributes(self):
        v = LengthValidator(min_length=0, max_length=3, debug=True, logger=False)
        self.assertEqual(v.min_length, 0)
        self.assertEqual(v.max_length, 3)
        self.assertIsNone(v.length)
        v.validate(None, "")
        v.validate(None, "abc")
        with self.assertRaises(ValueError):
            v.validate(None, "abcd")

    def test_string_validator_readme_max_length_happy_path(self):
        @dataclass
        class User(object):
            name: str = StringValidator(
                logger=False, debug=True, max_length=50, required=True
            )

        self.assertEqual(User(name="Ada").name, "Ada")
        with self.assertRaises(ValueError):
            User(name="x" * 51)

    def test_string_validator_min_value_override_still_runs(self):
        @dataclass
        class Ranked(object):
            name: str = StringValidator(min_value="B", debug=True, logger=False)

        self.assertEqual(Ranked(name="Cat").name, "Cat")
        with self.assertRaises(ValueError):
            Ranked(name="Ace")

    def test_integer_validator_value_and_multiple_keep(self):
        @dataclass
        class Count(object):
            n: int = IntegerValidator(
                min_value=0, max_value=10, multiple_of=2, debug=True, logger=False
            )

        self.assertEqual(Count(n=0).n, 0)
        self.assertEqual(Count(n=10).n, 10)
        with self.assertRaises(ValueError):
            Count(n=-2)
        with self.assertRaises(ValueError):
            Count(n=3)

    def test_validator_facade_accepts_value_and_length_kwargs(self):
        @dataclass
        class Sized(object):
            s: str = Validator(min_length=0, max_length=3, debug=True, logger=False)

        self.assertEqual(Sized(s="A").s, "A")
        self.assertEqual(Sized(s="").s, "")
        with self.assertRaises(ValueError):
            Sized(s="abcd")

        @dataclass
        class Ranked(object):
            s: str = Validator(min_value="A", max_value="Z", debug=True, logger=False)

        self.assertEqual(Ranked(s="A").s, "A")
        with self.assertRaises(ValueError):
            Ranked(s="0")


class TestSoft9ZeroStillConflicts(unittest.TestCase):
    """Soft #8: 0 is a bound, so exclusive pairs still conflict at 0."""

    def test_min_value_zero_and_gt_zero_conflict(self):
        with self.assertRaises(ValueError):
            ValueValidator(min_value=0, gt=0, debug=True, logger=False)
        with self.assertRaises(ValueError):
            MinValueValidator(min_value=0, gt=0, debug=True, logger=False)

    def test_max_value_zero_and_lt_zero_conflict(self):
        with self.assertRaises(ValueError):
            ValueValidator(max_value=0, lt=0, debug=True, logger=False)
        with self.assertRaises(ValueError):
            MaxValueValidator(max_value=0, lt=0, debug=True, logger=False)

    def test_value_and_eq_zero_conflict(self):
        with self.assertRaises(ValueError):
            ValueValidator(value=0, eq=0, debug=True, logger=False)

    def test_equal_zero_range_is_allowed(self):
        v = ValueValidator(min_value=0, max_value=0, debug=True, logger=False)
        v.validate(None, 0)
        with self.assertRaises(ValueError):
            v.validate(None, 1)
        length = LengthValidator(min_length=0, max_length=0, debug=True, logger=False)
        length.validate(None, "")
        with self.assertRaises(ValueError):
            length.validate(None, "x")


class TestSoft9SourceLocks(unittest.TestCase):
    """Readability lock: bound pairs use None-only all(...), never truthy all([...])."""

    def test_bound_facades_use_all_specified_not_truthy_and(self):
        src = VALIDATORS_PATH.read_text(encoding="utf-8")
        self.assertNotIn("all([min_value, max_value])", src)
        self.assertNotIn("all([min_length, max_length])", src)
        self.assertNotIn("and self.min_value\n", src)
        self.assertIn("class ValueValidator(ValidateProperty):", src)
        self.assertIn("class LengthValidator(ValidateProperty):", src)
        bases = {
            node.name: [ast.unparse(base) for base in node.bases]
            for node in ast.parse(src).body
            if isinstance(node, ast.ClassDef)
        }
        self.assertEqual(bases["ValueValidator"], ["ValidateProperty"])
        self.assertEqual(bases["LengthValidator"], ["ValidateProperty"])

    def test_leaf_multiple_of_zero_source_still_honest(self):
        src = inspect.getsource(MultipleValidator._validate_multiple_of)
        self.assertIn("multiple_of is not None", src)
        self.assertIn("value % multiple_of == 0", src)


if __name__ == "__main__":
    unittest.main()
