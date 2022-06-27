# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import abc
import datetime
import pathlib
from dataclasses import dataclass, make_dataclass
from typing import Any, Type

from valio.regexer.regexps import IfFollowedBy, Pattern, PatternType
from valio.regexer.relib import DigitGroups, WordGroups
from valio.validator import validators

REGEX_MAP = {str: WordGroups, int: DigitGroups}

__all__ = [
    "BytesSchema",
    "BooleanSchema",
    "IntegerSchema",
    "FloatSchema",
    "CharSchema",
    "FileSchema",
    "DateSchema",
    "EmailSchema",
    "PhoneNumberSchema",
    "PaymentCardSchema",
    "SchemaMixin",
]


class SchemaValidator(object):
    name = validators.StringValidator(logger=False)
    validator = Type[validators.Validator]
    annotation = Any

    def __set_name__(self, owner, name):
        self.name = name
        self.validator = make_dataclass(
            "validator", [(self.name, self.annotation, self.validator(**self.kwargs))]
        )

    def __init__(self, **kwargs):
        self.name = kwargs.pop("name", None) or self.name or type(self).__name__
        self.kwargs = kwargs


class SchemaBase(SchemaValidator):

    def _is_valid(self, *args):
        for v in args:
            self.validator(v)

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, args):
        self._is_valid(*args)
        self._args = args

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        regex_map = (
            {self.annotation: REGEX_MAP[self.annotation]}
            if self.annotation in REGEX_MAP
            else {
                self.annotation: {
                    v: REGEX_MAP[self.__class__.__dict__[v].annotation]
                    for v in self.__class__.__dict__
                    if isinstance(self.__class__.__dict__[v], SchemaBase)
                       and self.__class__.__dict__[v].annotation in REGEX_MAP
                }
            }
        )

        self.regex = (
            REGEX_MAP[self.annotation](
                count_min=self.kwargs.get("min_length", None),
                count_max=self.kwargs.get("max_length", None),
                name=str(self),
            ).named_capturing_group
            if self.annotation in REGEX_MAP
            else regex_map[self.annotation]
        )
        if isinstance(self.regex, dict):
            self.regex.update({k: getattr(self, k).regex for k in self.regex})

        pattern_field = self.kwargs.get("pattern", None)
        if pattern_field is not None and not isinstance(
                pattern_field, (str, PatternType)
        ):
            raise TypeError(
                f"expected 'pattern' of {str.__name__} or {Pattern.__name__} types,"
                f" got {type(pattern_field).__name__} type instead"
            )
        if not isinstance(self.regex, dict):
            if any(
                    {
                        v: getattr(pattern_field, v)
                        for v in self.__class__.__dict__
                        if (
                            isinstance(self.__class__.__dict__[v], SchemaBase)
                            and getattr(pattern_field, v, None) is not None
                    )
                    }
            ):
                raise AttributeError(
                    f"{self.regex.__name__} and {pattern_field.__name__} fields did not match"
                )

        regex = (
            (
                self.regex
                if pattern_field is None
                else IfFollowedBy(Pattern(pattern=pattern_field)) & self.regex
                if not isinstance(pattern_field, PatternType)
                else IfFollowedBy(pattern=pattern_field) & self.regex
            )
            if not isinstance(self.regex, dict)
            else {
                k: self.regex[k] & getattr(pattern_field, k)
                if getattr(pattern_field, k, None) is not None
                else self.regex[k]
                for k in self.regex
            }
        )

        self.regex = regex

        super(SchemaBase, self).__init__(**self.kwargs)
        if hasattr(self, "schema"):
            self._validate = getattr(self, "schema")

        self.args = args

    def __str__(self):
        return self.kwargs.get("name", None) or self.name or str(type(self).__name__)

    def __repr__(self):
        return f"{self.__str__()}({self.kwargs})"

    def __iter__(self):
        return iter(self.args)

    def __next__(self):
        return next(self)

    def __call__(self, *value):
        self.args = value
        return value


class BytesSchema(SchemaBase):
    annotation = bytes
    validator = validators.BytesValidator


class BooleanSchema(SchemaBase):
    annotation = bool
    validator = validators.BooleanValidator


class NumberSchema(SchemaBase):
    pass


class IntegerSchema(NumberSchema):
    annotation = int
    validator = validators.IntegerValidator


class PositiveIntegerSchema(IntegerSchema):
    def __init__(self, *args, **kwargs):
        super(PositiveIntegerSchema, self).__init__(*args, min_value=0, **kwargs)


class NegativeIntegerSchema(IntegerSchema):
    def __init__(self, *args, **kwargs):
        super(NegativeIntegerSchema, self).__init__(*args, max_value=0, **kwargs)


class FloatSchema(NumberSchema):
    annotation = float
    validator = validators.FloatValidator


class PositiveFloatSchema(FloatSchema):
    def __init__(self, *args, **kwargs):
        super(PositiveFloatSchema, self).__init__(*args, min_value=0.0, **kwargs)


class NegativeFloatSchema(FloatSchema):
    def __init__(self, *args, **kwargs):
        super(NegativeFloatSchema, self).__init__(*args, max_value=0.0, **kwargs)


class CharSchema(SchemaBase):
    annotation = str
    validator = validators.StringValidator


class DateSchema(SchemaBase):
    annotation = datetime.datetime
    validator = validators.DateValidator


class FileSchema(SchemaBase):
    annotation = pathlib.Path
    validators = validators.PathValidator


class EmailSchema(SchemaBase):
    annotation = str
    validator = validators.EmailIDValidator


class PaymentCardSchema(SchemaBase):
    annotation = str
    validator = validators.PaymentCardValidator


class PhoneNumberSchema(SchemaBase):
    annotation = str
    validator = validators.PhoneNumberValidator


class SchemaMixin(SchemaBase, abc.ABC):
    def __init__(self, *args, **kwargs):
        super(SchemaMixin, self).__init__(*args, **kwargs)

    @abc.abstractmethod
    def schema(self, *args, **kwargs):
        pass


if __name__ == "__main__":
    from secrets import compare_digest


    @dataclass
    class PasswordField(object):
        password: str
        confirm_password: str
        schema: "PasswordSchema" = None

        def __str__(self):
            raise PermissionError("permission denied")

        def __post_init__(self):
            self.schema(self)


    class PasswordSchema(SchemaMixin):
        password = CharSchema(
            min_length=5,
            max_length=32,
            pattern=Pattern(r"\d+\w+"),
            not_in_choice=["", '', "", "*"],
            logger=True,
            debug=True,
        )
        confirm_password = CharSchema(
            min_length=5,
            max_length=32,
            pattern=Pattern(r"\d+\w+"),
            logger=True,
            debug=True
        )
        annotation = PasswordField

        def schema(self, password: PasswordField):
            self.password(password.password)
            self.confirm_password(password.confirm_password)
            if not compare_digest(password.password, password.confirm_password):
                raise ValueError(
                    f"{self.password.name} and {self.confirm_password.name} did not match"
                )


    PasswordField.schema = PasswordSchema()
    password_ = PasswordField("9989z", "9989z")
    print(password_.schema)
