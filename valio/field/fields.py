# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT



from typing import Type, Union

from valio import validator as _validator
from valio.descriptor import DEBUG, DEFAULT, DOC, NAME
from valio.error import errors
from valio.logger import LOG_DIR, LOG_LEVEL, LOGGER, loggers
from valio.validator import (BOOL, BYTES, DATE_TIME_DELTA, FLOAT, INT, PATTERN,
                             STR, VALUE, UUID_Type)

# from tortoise import fields


__all__ = [
    "FieldMixin",
    "Field",
    "IntegerField",
    "FloatField",
    "DecimalField",
    "BytesField",
    "BooleanField",
    "StringField",
    "DateField",
    "EmailField",
    "PathField",
    "AadhaarCardField",
    "PaymentCardField",
    "PhoneNumberField",
    "IP4AddressField",
    "IP6AddressField",
    "IPAnyAddressField",
    "UUIDField",
    "EnumField",
    "IntegerEnumField",
    "StringEnumField"
]

_logger = dict()


class FieldBase(loggers.Logger):
    """This class provides base class for all the Field related stuffs"""

    def __set_name__(self, owner, name):
        self.name = name
        _logger[hex(id(self))] = self.get_logger(owner.__name__, name)

    def __class_getitem__(cls, key):
        """getattr"""
        if logger := _logger.get(hex(id(cls)), None):
            logger.info(f"{cls}: getting: {key}")
        try:
            if key not in cls.__dict__:
                raise AttributeError(key)
            return cls.__dict__[key]
        except (errors.GetAttributeError, Exception) as ge:
            if logger:
                logger.error(ge)
            raise ge

    def __setattr__(self, key, value):
        """setattr"""
        if logger := _logger.get(hex(id(self)), None):
            logger.info(f"{self}: setting: {key}")
        try:
            object.__setattr__(self, key, value)
        except (errors.SetAttributeError, Exception) as se:
            if logger:
                logger.error(se)
            raise se

    def __getattr__(self, key):
        """getattr"""
        if logger := _logger.get(hex(id(self)), None):
            logger.info(f"{self}: getting: {key}")
        try:
            if key not in self.__dict__:
                if key not in type(self).__dict__:
                    raise AttributeError(key)
                return type(self).__dict__[key]
            return self.__dict__[key]
        except (errors.GetAttributeError, Exception) as ge:
            if logger:
                logger.error(ge)
            raise ge

    def __delattr__(self, key):
        """delattr"""
        if logger := _logger.get(hex(id(self)), None):
            logger.info(f"{self}: deleting: {key}")
        try:
            del self.__dict__[key]
        except (errors.DeleteAttributeError, Exception) as de:
            if logger:
                logger.error(de)
            raise de

    __getitem__ = __getattr__
    __setitem__ = __setattr__

VALIDATOR = Union[Type[_validator.Validator], _validator.Validator]

class FieldMixin(FieldBase):
    validator: VALIDATOR

    def __init__(
            self,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
    ):
        super(FieldMixin, self).__init__(
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
        )

    def add_validator(self, func):
        self.validator.add_validator(func)
        return func

    def add_pre_validator(self, func):
        self.validator.add_pre_validator(func)
        return func

    def add_post_validator(self, func):
        self.validator.add_post_validator(func)
        return func

    def add_post_set(self, func):
        self.validator.add_post_set(func)
        return func

    def add_pre_get(self, func):
        self.validator.add_pre_get(func)
        return func

    def add_post_get(self, func):
        self.validator.add_post_get(func)
        return func

    def add_pre_delete(self, func):
        self.validator.add_pre_delete(func)
        return func

    def add_post_delete(self, func):
        self.validator.add_post_delete(func)
        return func

    def add_pre_validator_task(self, func):
        self.validator.add_pre_validator_task(func)
        return func

    def add_post_validator_task(self, func):
        self.validator.add_post_validator_task(func)
        return func

    def add_post_set_task(self, func):
        self.validator.add_post_set_task(func)
        return func

    def add_pre_get_task(self, func):
        self.validator.add_pre_get_task(func)
        return func

    def add_post_get_task(self, func):
        self.validator.add_post_get_task(func)
        return func

    def add_pre_delete_task(self, func):
        self.validator.add_pre_delete_task(func)
        return func

    def add_post_delete_task(self, func):
        self.validator.add_post_delete_task(func)
        return func

    def __str__(self):
        return f"{self.validator}"

    def __repr__(self):
        return self.__str__()


class Field(FieldMixin):
    validator: VALIDATOR = _validator.Validator

    def __init__(
            self,
            default: DEFAULT = None,
            name: NAME = None,
            doc: DOC = None,
            required: BOOL = None,
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
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            debug: DEBUG = None,
            enable_async: BOOL = None,
            **kwargs,
    ):
        self.validator = self.validator(
            default=default,
            name=name,
            doc=doc,
            required=required,
            pattern=pattern,
            reassign=reassign,
            min_value=min_value,
            value=value,
            max_value=max_value,
            min_length=min_length,
            length=length,
            max_length=max_length,
            expire_after=expire_after,
            expire_on=expire_on,
            expire_before=expire_before,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            debug=debug,
            enable_async=enable_async,
            **kwargs,
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class IntegerField(FieldMixin):
    validator: VALIDATOR = _validator.IntegerValidator

    def __init__(
            self,
            name: NAME = None,
            default: INT = None,
            required: BOOL = None,
            pattern: PATTERN = None,
            reassign: BOOL = None,
            min_value: INT = None,
            value: INT = None,
            max_value: INT = None,
            min_length: INT = None,
            length: INT = None,
            max_length: INT = None,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            debug: DEBUG = None,
            enable_async: BOOL = None,
            **kwargs,
    ):
        self.validator = self.validator(
            name=name,
            default=default,
            required=required,
            pattern=pattern,
            reassign=reassign,
            min_value=min_value,
            value=value,
            max_value=max_value,
            min_length=min_length,
            length=length,
            max_length=max_length,
            expire_after=expire_after,
            expire_on=expire_on,
            expire_before=expire_before,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            debug=debug,
            enable_async=enable_async,
            **kwargs,
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class FloatField(FieldMixin):
    validator: VALIDATOR = _validator.FloatValidator

    def __init__(
            self,
            name: NAME = None,
            default: FLOAT = None,
            required: BOOL = None,
            pattern: PATTERN = None,
            reassign: BOOL = None,
            min_value: FLOAT = None,
            value: FLOAT = None,
            max_value: FLOAT = None,
            min_length: INT = None,
            length: INT = None,
            max_length: INT = None,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            debug: DEBUG = None,
            enable_async: BOOL = None,
            **kwargs,
    ):
        self.validator = self.validator(
            name=name,
            default=default,
            required=required,
            pattern=pattern,
            reassign=reassign,
            min_value=min_value,
            value=value,
            max_value=max_value,
            min_length=min_length,
            length=length,
            max_length=max_length,
            expire_after=expire_after,
            expire_on=expire_on,
            expire_before=expire_before,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            debug=debug,
            enable_async=enable_async,
            **kwargs,
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class DecimalField(FieldMixin):
    validator: VALIDATOR = _validator.DecimalValidator

    def __init__(
            self,
            name: NAME = None,
            default: FLOAT = None,
            required: BOOL = None,
            pattern: PATTERN = None,
            reassign: BOOL = None,
            min_value: FLOAT = None,
            value: FLOAT = None,
            max_value: FLOAT = None,
            min_length: INT = None,
            length: INT = None,
            max_length: INT = None,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            debug: DEBUG = None,
            enable_async: BOOL = None,
            **kwargs,
    ):
        self.validator = self.validator(
            name=name,
            default=default,
            required=required,
            pattern=pattern,
            reassign=reassign,
            min_value=min_value,
            value=value,
            max_value=max_value,
            min_length=min_length,
            length=length,
            max_length=max_length,
            expire_after=expire_after,
            expire_on=expire_on,
            expire_before=expire_before,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            debug=debug,
            enable_async=enable_async,
            **kwargs,
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class BooleanField(FieldMixin):
    validator: VALIDATOR = _validator.BooleanValidator

    def __init__(
            self,
            name: NAME = None,
            default: BOOL = None,
            required: BOOL = None,
            reassign: BOOL = None,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            debug: DEBUG = None,
            enable_async: BOOL = None,
            **kwargs,
    ):
        self.validator = self.validator(
            name=name,
            default=default,
            required=required,
            reassign=reassign,
            expire_after=expire_after,
            expire_on=expire_on,
            expire_before=expire_before,
            debug=debug,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            enable_async=enable_async,
            **kwargs,
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class BytesField(FieldMixin):
    validator: VALIDATOR = _validator.BytesValidator

    def __init__(
            self,
            name: NAME = None,
            default: BYTES = None,
            required: BOOL = None,
            pattern: PATTERN = None,
            reassign: BOOL = None,
            min_value: BYTES = None,
            max_value: BYTES = None,
            min_length: INT = None,
            max_length: INT = None,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            debug: DEBUG = None,
            enable_async: BOOL = None,
            **kwargs,
    ):
        self.validator = self.validator(
            name=name,
            default=default,
            required=required,
            pattern=pattern,
            reassign=reassign,
            min_value=min_value,
            max_value=max_value,
            min_length=min_length,
            max_length=max_length,
            expire_after=expire_after,
            expire_on=expire_on,
            expire_before=expire_before,
            debug=debug,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            enable_async=enable_async,
            **kwargs,
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class StringField(FieldMixin):
    validator: VALIDATOR = _validator.StringValidator

    def __init__(
            self,
            name: NAME = None,
            default: STR = None,
            required: BOOL = None,
            pattern: PATTERN = None,
            reassign: BOOL = None,
            min_value: STR = None,
            value: STR = None,
            max_value: STR = None,
            min_length: INT = None,
            length: INT = None,
            max_length: INT = None,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            debug: DEBUG = None,
            enable_async: BOOL = None,
            **kwargs,
    ):
        self.validator = self.validator(
            name=name,
            default=default,
            required=required,
            pattern=pattern,
            reassign=reassign,
            min_value=min_value,
            value=value,
            max_value=max_value,
            min_length=min_length,
            length=length,
            max_length=max_length,
            expire_after=expire_after,
            expire_on=expire_on,
            expire_before=expire_before,
            debug=debug,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            enable_async=enable_async,
            **kwargs,
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class DateField(FieldMixin):
    validator: VALIDATOR = _validator.DateValidator

    def __init__(
            self,
            name: NAME = None,
            default: DATE_TIME_DELTA = None,
            required: BOOL = None,
            reassign: BOOL = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            debug: DEBUG = None,
            enable_async: BOOL = None,
            **kwargs,
    ):
        self.validator = self.validator(
            name=name,
            default=default,
            required=required,
            reassign=reassign,
            debug=debug,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            enable_async=enable_async,
            **kwargs
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class PathField(FieldMixin):
    validator: VALIDATOR = _validator.PathValidator

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            pattern: PATTERN = None,
            min_length: INT = None,
            length: INT = None,
            max_length: INT = None,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs,
    ):
        self.validator = self.validator(
            default=default,
            required=required,
            reassign=reassign,
            pattern=pattern,
            min_length=min_length,
            length=length,
            max_length=max_length,
            expire_after=expire_after,
            expire_on=expire_on,
            expire_before=expire_before,
            name=name,
            doc=doc,
            debug=debug,
            **kwargs,
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class IP4AddressField(FieldMixin):
    validator: VALIDATOR = _validator.IP4AddressValidator

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            pattern: PATTERN = None,
            min_value: STR = None,
            value: STR = None,
            max_value: STR = None,
            min_length: INT = None,
            length: INT = None,
            max_length: INT = None,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs,
    ):
        self.validator = self.validator(
            default=default,
            required=required,
            reassign=reassign,
            pattern=pattern,
            min_value=min_value,
            value=value,
            max_value=max_value,
            min_length=min_length,
            length=length,
            max_length=max_length,
            expire_after=expire_after,
            expire_on=expire_on,
            expire_before=expire_before,
            name=name,
            doc=doc,
            debug=debug,
            **kwargs,
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class IP6AddressField(FieldMixin):
    validator: VALIDATOR = _validator.IP6AddressValidator

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            pattern: PATTERN = None,
            min_value: STR = None,
            value: STR = None,
            max_value: STR = None,
            min_length: INT = None,
            length: INT = None,
            max_length: INT = None,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs,
    ):
        self.validator = self.validator(
            default=default,
            required=required,
            reassign=reassign,
            pattern=pattern,
            min_value=min_value,
            value=value,
            max_value=max_value,
            min_length=min_length,
            length=length,
            max_length=max_length,
            expire_after=expire_after,
            expire_on=expire_on,
            expire_before=expire_before,
            name=name,
            doc=doc,
            debug=debug,
            **kwargs,
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class IPAnyAddressField(FieldMixin):
    validator: VALIDATOR = _validator.IPAnyAddressValidator

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            pattern: PATTERN = None,
            min_value: STR = None,
            value: STR = None,
            max_value: STR = None,
            min_length: INT = None,
            length: INT = None,
            max_length: INT = None,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs,
    ):
        self.validator = self.validator(
            default=default,
            required=required,
            reassign=reassign,
            pattern=pattern,
            min_value=min_value,
            value=value,
            max_value=max_value,
            min_length=min_length,
            length=length,
            max_length=max_length,
            expire_after=expire_after,
            expire_on=expire_on,
            expire_before=expire_before,
            name=name,
            doc=doc,
            debug=debug,
            **kwargs,
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class EmailField(FieldMixin):
    validator: VALIDATOR = _validator.EmailIDValidator

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs
    ):
        self.validator = self.validator(
            default=default,
            required=required,
            reassign=reassign,
            name=name,
            doc=doc,
            debug=debug,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            **kwargs
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class AadhaarCardField(FieldMixin):
    validator: VALIDATOR = _validator.AadhaarCardValidator

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs
    ):
        self.validator = self.validator(
            default=default,
            required=required,
            reassign=reassign,
            name=name,
            doc=doc,
            debug=debug,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            **kwargs
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class PaymentCardField(FieldMixin):
    validator: VALIDATOR = _validator.PaymentCardValidator

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs
    ):
        self.validator = self.validator(
            default=default,
            required=required,
            reassign=reassign,
            name=name,
            doc=doc,
            debug=debug,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            **kwargs
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class PhoneNumberField(FieldMixin):
    validator: VALIDATOR = _validator.PhoneNumberValidator

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs
    ):
        self.validator = self.validator(
            default=default,
            required=required,
            reassign=reassign,
            name=name,
            doc=doc,
            debug=debug,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            **kwargs
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class UUIDField(FieldMixin):
    validator: VALIDATOR = _validator.UUIDValidator

    def __init__(
            self,
            name: NAME = None,
            default: UUID_Type = None,
            required: BOOL = None,
            reassign: BOOL = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            debug: DEBUG = None,
            enable_async: BOOL = None,
            **kwargs,
    ):
        self.validator = self.validator(
            name=name,
            default=default,
            required=required,
            reassign=reassign,
            debug=debug,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            enable_async=enable_async,
            **kwargs
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class EnumField(FieldMixin):
    validator: VALIDATOR = _validator.EnumValidator

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs
    ):
        self.validator = self.validator(
            default=default,
            required=required,
            reassign=reassign,
            name=name,
            doc=doc,
            debug=debug,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            **kwargs
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class IntegerEnumField(FieldMixin):
    validator: VALIDATOR = _validator.IntegerEnumValidator

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs
    ):
        self.validator = self.validator(
            default=default,
            required=required,
            reassign=reassign,
            name=name,
            doc=doc,
            debug=debug,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            **kwargs
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)


class StringEnumField(FieldMixin):
    validator: VALIDATOR = _validator.StringEnumValidator

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs
    ):
        self.validator = self.validator(
            default=default,
            required=required,
            reassign=reassign,
            name=name,
            doc=doc,
            debug=debug,
            logger=logger,
            log_levels=log_levels,
            log_dir=log_dir,
            **kwargs
        )

        FieldMixin.__init__(self, logger=logger, log_levels=log_levels, log_dir=log_dir)
