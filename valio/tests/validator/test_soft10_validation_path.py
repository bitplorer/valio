# Copyright (c) 2022 Valio
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""Soft #10: full validation-path composability (deeper than Soft #9)."""

import ast
import inspect
import pathlib
import unittest
from dataclasses import dataclass

from valio.validator import validators as validators_mod
from valio.validator.validators import (
    AttributeValidator,
    ChoiceValidator,
    ExpiryValidator,
    IntegerValidator,
    LengthValidator,
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    MultipleValidator,
    PatternValidator,
    ReassignValidator,
    RequiredValidator,
    StringValidator,
    TaskValidator,
    TypeValidator,
    ValidateProperty,
    Validator,
    ValueValidator,
)


VALIDATORS_PATH = pathlib.Path(validators_mod.__file__)

CONCERN_LEAVES = (
    TypeValidator,
    RequiredValidator,
    PatternValidator,
    ReassignValidator,
    MultipleValidator,
    ValueValidator,
    LengthValidator,
    ExpiryValidator,
    ChoiceValidator,
    AttributeValidator,
    TaskValidator,
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
)

DEFAULT_PATH_NAMES = (
    "reassignment",
    "type",
    "required",
    "pattern",
    "multiple_of",
    "length",
    "value",
    "expiry",
    "choice",
    "attribute",
)


def _class_bases():
    src = VALIDATORS_PATH.read_text(encoding="utf-8")
    return {
        node.name: [ast.unparse(base) for base in node.bases]
        for node in ast.parse(src).body
        if isinstance(node, ast.ClassDef)
    }


class TestSoft10MegaValidatorComposesLeaves(unittest.TestCase):
    """Mega-validator assembles concerns; it does not dual-inherit them."""

    def test_validator_does_not_inherit_concern_leaves(self):
        for leaf in CONCERN_LEAVES:
            self.assertFalse(issubclass(Validator, leaf), leaf.__name__)
        self.assertTrue(issubclass(Validator, ValidateProperty))

    def test_typed_aliases_still_subclass_validator(self):
        self.assertTrue(issubclass(IntegerValidator, Validator))
        self.assertTrue(issubclass(StringValidator, Validator))

    def test_value_length_still_compose_min_max_leaves(self):
        self.assertFalse(issubclass(ValueValidator, MinValueValidator))
        self.assertFalse(issubclass(ValueValidator, MaxValueValidator))
        self.assertFalse(issubclass(LengthValidator, MinLengthValidator))
        self.assertFalse(issubclass(LengthValidator, MaxLengthValidator))
        self.assertTrue(issubclass(ValueValidator, ValidateProperty))
        self.assertTrue(issubclass(LengthValidator, ValidateProperty))

    def test_ast_validator_bases_are_validate_property_only(self):
        bases = _class_bases()
        self.assertEqual(bases["Validator"], ["ValidateProperty"])
        self.assertEqual(bases["ValueValidator"], ["ValidateProperty"])
        self.assertEqual(bases["LengthValidator"], ["ValidateProperty"])


class TestSoft10ValidationPathFailClosed(unittest.TestCase):
    """Wrong order / double-call / nested leaf+aggregate fail closed."""

    def test_path_helper_exists(self):
        self.assertTrue(hasattr(validators_mod, "_ValidationPath"))

    def test_duplicate_unit_fails_closed(self):
        with self.assertRaises(ValueError) as ctx:
            validators_mod._ValidationPath(("value", "value"))
        self.assertIn("double-call", str(ctx.exception))

    def test_aggregate_plus_owned_leaf_fails_closed(self):
        with self.assertRaises(ValueError) as ctx:
            validators_mod._ValidationPath(("value", "min_value"))
        self.assertIn("conflict", str(ctx.exception))
        with self.assertRaises(ValueError):
            validators_mod._ValidationPath(("length", "max_length"))

    def test_default_validator_path_is_unique_and_ordered(self):
        self.assertTrue(hasattr(Validator, "_validation_path"))
        self.assertEqual(tuple(Validator._validation_path.names), DEFAULT_PATH_NAMES)
        self.assertEqual(
            len(Validator._validation_path.names),
            len(set(Validator._validation_path.names)),
        )

    def test_path_run_is_per_pass_so_a_second_validate_is_allowed(self):
        calls = []

        def _once(owner, instance, value):
            calls.append(value)
            return value

        path = validators_mod._ValidationPath(("type",))
        path.run(None, None, 1, {"type": _once})
        path.run(None, None, 2, {"type": _once})
        self.assertEqual(calls, [1, 2])

    def test_path_run_refuses_duplicate_names_inside_one_pass(self):
        path = validators_mod._ValidationPath(("type",))
        path.names = ("type", "type")
        with self.assertRaises(ValueError) as ctx:
            path.run(None, None, 1, {"type": lambda *args: None})
        self.assertIn("double-call", str(ctx.exception))


class TestSoft10PublicUsageKeep(unittest.TestCase):
    """Public kwargs, attributes, and README-shaped happy paths KEEP."""

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

    def test_reassign_false_still_blocks_second_assign(self):
        @dataclass
        class Once(object):
            s: str = Validator(reassign=False, debug=True, logger=False)

        once = Once(s="a")
        self.assertEqual(once.s, "a")
        with self.assertRaises(AttributeError):
            once.s = "b"

    def test_in_choice_still_enforced(self):
        @dataclass
        class Picked(object):
            s: str = Validator(
                in_choice=["Male", "Female", "Trans"], debug=True, logger=False
            )

        self.assertEqual(Picked(s="Female").s, "Female")
        with self.assertRaises(ValueError):
            Picked(s="Other")


class TestSoft10BoundHonestyKeep(unittest.TestCase):
    """Soft #8 via the composed facade: 0 is a bound; gt/lt exclusive."""

    def test_validator_min_value_zero_gt_zero_conflicts(self):
        with self.assertRaises(ValueError):
            Validator(min_value=0, gt=0, debug=True, logger=False)

    def test_validator_max_value_zero_lt_zero_conflicts(self):
        with self.assertRaises(ValueError):
            Validator(max_value=0, lt=0, debug=True, logger=False)

    def test_validator_min_value_zero_enforces(self):
        v = Validator(min_value=0, debug=True, logger=False)
        self.assertEqual(v.min_value, 0)
        v.validate(None, 0)
        with self.assertRaises(ValueError):
            v.validate(None, -1)

    def test_length_zero_still_enforces_on_facade(self):
        v = Validator(length=0, debug=True, logger=False)
        v.validate(None, "")
        with self.assertRaises(ValueError):
            v.validate(None, "x")

    def test_multiple_of_zero_still_safe_on_facade(self):
        v = Validator(multiple_of=0, debug=True, logger=False)
        self.assertEqual(v.multiple_of, 0)
        v.validate(None, 0)
        with self.assertRaises(ValueError):
            v.validate(None, 1)


class TestSoft10SourceLocks(unittest.TestCase):
    """Assembly is a path of units; bound gates stay None-only."""

    def test_validate_field_runs_the_path_not_an_ad_hoc_list(self):
        src = inspect.getsource(Validator._validate_field)
        self.assertIn("_validation_path", src)
        self.assertNotIn("self._validate_reassignment(instance, value)", src)
        self.assertNotIn("self._validate_length(instance, value)", src)
        self.assertNotIn("self._validate_value(instance, value)", src)

    def test_string_min_value_uses_shared_bound_helper(self):
        src = inspect.getsource(StringValidator._validate_min_value)
        self.assertIn("_enforce_min_bound", src)
        self.assertNotIn("value < min_value", src)

    def test_exclusive_pairs_go_through_all_specified(self):
        src = inspect.getsource(validators_mod._reject_exclusive)
        self.assertIn("_all_specified", src)

    def test_all_specified_still_none_only(self):
        src = inspect.getsource(validators_mod._all_specified)
        self.assertIn("all(bound is not None for bound in bounds)", src)
        self.assertNotIn("all([", src)


if __name__ == "__main__":
    unittest.main()
