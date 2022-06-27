# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT




import pathlib

from valio.descriptor import DEBUG, DEFAULT, DOC, NAME
from valio.field import fields
from valio.logger import LOG_DIR, LOG_LEVEL, LOGGER
from valio.regexer import regexps
from valio.regexer.relib import patterns
from valio.validator import BOOL, DATE_TIME_DELTA, INT, PATTERN, VALUE

REGEX_MAP = {str: patterns.WordGroups, int: patterns.DigitGroups}


class Schema(fields.Field):
    """
    """
    annotation = None

    def __init__(
            self,
            name: NAME = None,
            default: DEFAULT = None,
            blank: BOOL = None,
            pattern: PATTERN = None,
            reassign: BOOL = None,
            min_value: VALUE = None,
            value: VALUE = None,
            max_value: VALUE = None,
            min_length: INT = None,
            length: INT = None,
            max_length: INT = None,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            debug: DEBUG = None,
            logger: LOGGER = None,
            log_dir: LOG_DIR = None,
            log_levels: LOG_LEVEL = None,
            doc: DOC = None,
            **kwargs,
    ):
        super(Schema, self).__init__(
            name=name,
            default=default,
            blank=blank,
            pattern=pattern,
            reassign=reassign,
            min_value=min_value,
            value=value,
            max_value=max_value,
            min_length=min_length,
            length=length,
            max_length=max_length,
            expire_before=expire_before,
            expire_on=expire_on,
            expire_after=expire_after,
            debug=debug,
            doc=doc,
            logger=logger,
            log_dir=log_dir,
            log_levels=log_levels,
            **kwargs,
        )

        # creating the regex mapping for types
        regex_map = (
            {self.annotation: REGEX_MAP[self.annotation]}
            if self.annotation in REGEX_MAP
            else {
                self.annotation: {
                    v: REGEX_MAP[self.__class__.__dict__[v].validator.annotation]
                    for v in self.__class__.__dict__
                    if isinstance(self.__class__.__dict__[v], Schema)
                       and self.__class__.__dict__[v].validator.annotation in REGEX_MAP
                }
            }
        )
        self.regex = (
            REGEX_MAP[self.annotation](
                count_min=min_length, count_max=max_length, name=name or str(self),
            ).named_capturing_group
            if self.annotation in REGEX_MAP
            else regex_map[self.annotation]
        )
        if isinstance(self.regex, dict):
            self.regex.update({k: getattr(self, k).regex for k in self.regex})

        if not isinstance(self.regex, dict):
            if any(
                    {
                        v: getattr(pattern, v)
                        for v in self.__class__.__dict__
                        if (
                            isinstance(self.__class__.__dict__[v], Schema)
                            and getattr(pattern, v, None) is not None
                    )
                    }
            ):
                raise AttributeError(
                    f"{self.regex.__name__} and {pattern.__name__} fields did not match"
                )

        _regex = (
            (
                self.regex
                if pattern is None
                else regexps.IfFollowedBy(regexps.Pattern(pattern)) & self.regex
                if not isinstance(pattern, regexps.PatternType)
                else regexps.IfFollowedBy(pattern) & self.regex
            )
            if not isinstance(self.regex, dict)
            else {
                k: self.regex[k] & getattr(pattern, k)
                if getattr(pattern, k, None) is not None
                else self.regex[k]
                for k in self.regex
            }
        )

        self.regex = _regex

    def __str__(self):
        return str(type(self).__name__)


class BytesSchema(Schema, fields.BytesField):
    """
    """
    annotation = bytes


class BooleanSchema(Schema, fields.BooleanField):
    """
    """
    annotation = bool


class NumberSchema(Schema):
    """
    """


class IntegerSchema(NumberSchema, fields.IntegerField):
    """
    """
    annotation = int


class FloatSchema(NumberSchema, fields.FloatField):
    """
    """
    annotation = float


class CharSchema(Schema, fields.StringField):
    """
    """
    annotation = str


class DateSchema(Schema, fields.DateField):
    """
    """


class FileSchema(Schema):
    annotation = pathlib.Path


if __name__ == "__main__":
    from dataclasses import dataclass
    from secrets import compare_digest


    @dataclass
    class Passwords(object):
        password_field = CharSchema(
            min_length=5,
            max_length=32,
            pattern=regexps.Pattern(r"[\d+\w+]"),
            debug=True,
        )
        confirm_password_field = CharSchema(
            min_length=5,
            max_length=32,
            pattern=regexps.Pattern(r"[\d+\w+]"),
            debug=True,
        )
        password: str = password_field.validator
        confirm_password: str = confirm_password_field.validator

        def __post_init__(self):
            if not compare_digest(self.password, self.confirm_password):
                raise ValueError(
                    f"{self.password_field.name} did not match {self.confirm_password_field.name}"
                )


    passwords = Passwords("aq1qq", "aq1qq")
    print(passwords.password_field.annotation)
