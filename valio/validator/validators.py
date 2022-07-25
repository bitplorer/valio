# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT



'''
MAKE SURE NOT TO IMPORT annotations from future else whole code gets minced
'''


import asyncio
import cProfile
import datetime
import decimal
import io
import ipaddress
import os
import pathlib
import pstats
import re
import sys
import typing
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, IntEnum
from functools import partial, wraps

if typing.TYPE_CHECKING:
    
    class TimedFunc(typing.Protocol):

            def __init__(self):...

            @property
            def lifetime(self):
                ...
                
            @lifetime.setter
            def lifetime(self, value):
                ...
            
            @property
            def expiration(self):
                ...
                
            @expiration.setter
            def expiration(self, value):
                ...
                
            def __call__(self): ...
    F = typing.TypeVar('F', bound=TimedFunc)
        
    def lru_cache(maxsize: int = 128, typed: bool = False) -> typing. Callable[[F], F]:
        pass
else:
    from functools import lru_cache
    F = typing.TypeVar('F', bound=typing.Callable[[typing.Any], typing.Any])

from uuid import UUID

import phonenumbers as phn
from typingx import isinstancex
from valio.descriptor import DEBUG, DEFAULT, DOC, NAME, descriptors
from valio.regexer import regexps, relib
from valio.regexer.relib.dates import (day_numbers, eu_date, get_date,
                                       ind_date, months_numbers)

__all__ = [
    "ValidateProperty",
    "TypeValidator",
    "RequiredValidator",
    "PatternValidator",
    "ReassignValidator",
    "MultipleValidator",
    "ValueValidator",
    "LengthValidator",
    "ExpiryValidator",
    "ChoiceValidator",
    "TaskValidator",
    "Validator",
    "IntegerValidator",
    "FloatValidator",
    "DecimalValidator",
    "BooleanValidator",
    "BytesValidator",
    "StringValidator",
    "HexShortColorValidator",
    "HexLongColorValidator",
    "HexColorValidator",
    "RGBOrRGBAColorValidator",
    "HSLOrHSLAColorValidator",
    "DateValidator",
    "PathValidator",
    "EmailIDValidator",
    "PaymentCardValidator",
    "PhoneNumberValidator",
    "AadhaarCardValidator",
    "PANCardValidator",
    "IP4AddressValidator",
    "IP6AddressValidator",
    "IPAnyAddressValidator",
    "SequenceValidator",
    "MappingValidator",
    "ListValidator",
    "DictionaryValidator",
    "SetValidator",
    "TupleValidator",
    "UUIDValidator",
    "EnumValidator",
    "IntegerEnumValidator",
    "StringEnumValidator",
    "INT",
    "FLOAT",
    "BYTES",
    "BOOL",
    "STR",
    "PATTERN",
    "VALUE",
    "DATE_TIME_DELTA",
    "TYPE",
    "UUID_Type",
    "CHOICE"
]


def profile(func):
    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        fd = io.StringIO()
        pr.enable()
        res = func(*args, *kwargs)
        pr.disable()
        sort_by = "cumulative"
        ps = pstats.Stats(pr, stream=fd).sort_stats(sort_by)
        ps.print_stats()
        module_name = os.path.splitext(
            os.path.basename(sys.modules["__main__"].__file__)
        )[0]
        join, cwd, exists = os.path.join, os.getcwd(), os.path.exists
        prof_dir = join(join(cwd, "profiles"), module_name)
        if not exists(prof_dir):
            os.makedirs(prof_dir)
        ps.dump_stats(f"{join(prof_dir, str(func.__name__))}.dat")
        print(fd.getvalue())
        return res

    return inner


def timed_lru_cache(seconds: int, maxsize: int = 128) -> typing.Callable[[F], typing.Callable[..., F]]:
    def wrapper_cache(func: F) ->  typing.Callable[..., F]:
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = datetime.timedelta(seconds=seconds)
        func.expiration = datetime.datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.datetime.utcnow() + func.lifetime
            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


class ValidateProperty(descriptors.Property, ABC):
    """Validation base class, it has abstract validate method
    which must be implemented by every inherited class.

    >>> class Validators(ValidateProperty):
    ...     # class that implements actual validation
    ...
    ...     def validate(self, instance=None, value=None):
    ...         return ...
    """
    
    def pre_set(self, obj, value):
        """
        :param obj: instance object of the assigned class
        :param value: the value that is being assigned
        :return:
        """
        try:
            value = self.pre_validation_processing(instance=obj, value=value)
            self.validate(instance=obj, value=value)
            value = self.post_validation_processing(instance=obj, value=value)
            return value
        except (Exception,) as pre_set_err:
            raise pre_set_err

    @abstractmethod
    def validate(self, instance=None, value=None):
        """Base Abstract Method for validation which is used for all
        validation purposes in the api.

        :param instance:
        :param value: undefined
        :return:
        """
        raise NotImplementedError(
            "Subclasses of ValidateProperty must implement the validate() method"
        )

    @classmethod
    def pre_validation_processing(cls, instance, value):
        """Base method which can be overridden for extraction,
        transformation or loading  pre-validation"""
        return value

    @classmethod
    def post_validation_processing(cls, instance, value):
        """Base method which can be overridden for extraction,
        transformation or loading  post-validation"""
        return value

    def post_set(self, obj, value):
        """When the value is set this method is called post setting
        of value

        :param obj:
        :param value:
        :return:
        """
        try:
            return self.post_set_processing(instance=obj, value=value)
        except (Exception,) as post_set_error:
            raise post_set_error

    @classmethod
    def post_set_processing(cls, instance, value):
        """Base method which can be overridden for extraction,
        transformation or loading  post-setting
        """
        return value

    def pre_get(self, obj, value):
        """When the value is get this method is called pre getting
        of value

        :param obj:
        :param value:
        :return:
        """
        try:
            return self.pre_get_processing(instance=obj, value=value)
        except (Exception,) as pre_get_error:
            raise pre_get_error

    @classmethod
    def pre_get_processing(cls, instance, value):
        """Base method which can be over ridden for extraction,
        transformation or loading  pre-getting
        """
        return value

    def post_get(self, obj, value):
        """When the value is get this method is called post getting
        of value

        :param obj:
        :param value:
        :return:
        """
        try:
            return self.post_get_processing(instance=obj, value=value)
        except (Exception,) as post_get_error:
            raise post_get_error

    @classmethod
    def post_get_processing(cls, instance, value):
        """Base method which can be over ridden for extraction,
        transformation or loading  post-getting
        """
        return value

    def pre_delete(self, obj, value):
        """When the value is get this method is called pre delete
        of value

        :param obj:
        :param value:
        :return:
        """
        try:
            return self.pre_delete_processing(instance=obj, value=value)
        except (Exception,) as pre_delete_error:
            raise pre_delete_error

    @classmethod
    def pre_delete_processing(cls, instance, value):
        """Base method which can be over ridden for extraction,
        transformation or loading  pre-delete
        """
        return value

    def post_delete(self, obj, value):
        """When the value is get this method is called post delete
        of value

        :param obj:
        :param value:
        :return:
        """
        try:
            return self.post_delete_processing(instance=obj, value=value)
        except (Exception,) as post_delete_error:
            raise post_delete_error

    @classmethod
    def post_delete_processing(cls, instance, value):
        """Base method which can be over ridden for extraction,
        transformation or loading  post-delete
        """
        return value
    

V = typing.TypeVar("V", bound=ValidateProperty)
T = typing.TypeVar("T")
Union = typing.Union[T, V, None]

PATH = Union[typing.Union[pathlib.Path, str], V]

# built-ins types
INT = Union[int, V]
FLOAT = Union[float, V]
DECIMAL = Union[decimal.Decimal, V]
BYTES = Union[bytes, V]
BOOL = Union[bool, V]
STR = Union[str, V]
CHOICE = Union[typing.Any, V]
PHONE_NUM = Union[str, V]
PATTERN = Union[typing.Union[str, regexps.PatternType], V]
VALUE = Union[typing.Union[int, float, bytes, str], V]
DATE_TIME_DELTA = Union[
    typing.Union[
        datetime.datetime,
        datetime.date,
        datetime.time,
        datetime.timedelta,
        str], V]

TYPE = Union[typing.Any, V]
LIST = Union[list, V]
DICT = Union[dict, V]
SET = Union[set, V]
TUPLE = Union[tuple, V]
ENUM = Union[Enum, V]
INT_ENUM = Union[IntEnum, V]
STR_ENUM = Union[typing.Union[str, Enum], V]
UUID_Type = Union[UUID, V]


@dataclass
class TypeValidator(ValidateProperty):
    """This class validates the expected type of the value given.

    Usage:

    >>> @dataclass
    ... class Ranges(ValidateProperty):
    ...     min_value: VALUE = TypeValidator(logger=False)
    ...     max_value: VALUE = TypeValidator(logger=False)
    ...
    ...     def __init__(
    ...         self,
    ...         min_value: VALUE = None,
    ...         max_value: VALUE = None,
    ...     ):
    ...
    ...         if min_value is not None:
    ...             self.min_value = min_value
    ...
    ...         if max_value is not None:
    ...             self.max_value = max_value
    ...
    ...         if all([min_value, max_value]) and max_value < min_value:
    ...             raise ValueError(f"max_value can not be less than min_value")
    ...
    ...         super(Ranges, self).__init__()
    ...
    ...     def validate(self, instance=None, value=None):
    ...         ...
    ...
    """

    def __init__(
            self,
            debug: DEBUG = None,
            doc: DOC = None,
            name: NAME = None,
            **kwargs,
    ):
        super(TypeValidator, self).__init__(debug=debug, doc=doc, name=name, **kwargs)

    def validate(self, instance=None, value=None):
        self._validate_type(instance, value)

    def _validate_type(self, instance, value):  # noqa
        if logger := self.logger:
            logger.info(f"{self.name}: Type: {self.annotation}")
        
        if self.annotation is not None:
            if value is not None and not isinstancex(value, self.annotation):
                raise TypeError(
                    f"{self.name} expect {self.annotation} type, "
                    f"got {type(value).__name__} type instead"
                )
                


@dataclass
class RequiredValidator(ValidateProperty):
    required: BOOL = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            required: BOOL = None,
            debug: DEBUG = None,
            doc: DOC = None,
            name: NAME = None,
            **kwargs,
    ): 
        self.required = required
        super(RequiredValidator, self).__init__(debug=debug, doc=doc, name=name, **kwargs)
        try:
            if self.required is not None:
                if self.doc is not None:
                    self.doc += f", required: {self.required}"
                else:
                    self.doc = f"required: {self.required}"
        except KeyError as ke:
            pass
        
    def validate(self, instance=None, value=None):
        self._validate_required(instance, value)

    def _validate_required(self, instance, value):  # noqa
        required = None
        try:
            if self.required is not None and self.required:
                required = self.required
        except KeyError as ke:
            pass
            
        if required:
            if logger := self.logger:
                logger.info(f"{self.name}: Required: {required}")
                
            if value is None:
                raise ValueError(
                    f"{self.name} requires value, got {value} instead"
                )


@dataclass
class PatternValidator(ValidateProperty):
    pattern: PATTERN = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            pattern: PATTERN = None,
            debug: DEBUG = None,
            doc: DOC = None,
            name: NAME = None,
            **kwargs,
    ):  
        self.pattern = pattern
            
        super(PatternValidator, self).__init__(debug=debug, doc=doc, name=name, **kwargs)
        try:
            if self.pattern is not None:
                if self.doc is not None:
                    self.doc += f", pattern: " \
                                f"{self.pattern if not isinstance(self.pattern, regexps.PatternType) else self.pattern.alias}"
                else:
                    self.doc = f"pattern: " \
                            f"{self.pattern if not isinstance(self.pattern, regexps.PatternType) else self.pattern.alias}"
        except KeyError as ke:
            pass
        
    def validate(self, instance=None, value=None):
        self._validate_pattern(instance, value)

    def _validate_pattern(self, instance, value):  # noqa
        pattern = None 
        try:
            if self.pattern is not None:
                pattern = (
                    self.pattern.pattern
                    if isinstance(self.pattern, regexps.PatternType)
                    else self.pattern
                )
        except KeyError as ke:
            pass
        if pattern:
            if logger := self.logger:
                logger.info(f"{self.name}: Regexp: {self.pattern}")

            if value is not None:
                value = value if isinstance(value, str) else str(value)
                get_pattern = re.compile(pattern).findall
                pattern = get_pattern(value)
                if not any(pattern):
                    raise ValueError(
                        f"{self.name} must have the pattern "
                        f"{self.pattern if not hasattr(self.pattern,'alias') else self.pattern.alias}"
                    )


@dataclass
class ReassignValidator(ValidateProperty):
    reassign: BOOL = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            reassign: BOOL = None,
            debug: DEBUG = None,
            doc: DOC = None,
            name: NAME = None,
            **kwargs,
    ):  
        self.number_of_assignment = None
        self.reassign = reassign
        
        super(ReassignValidator, self).__init__(debug=debug, doc=doc, name=name, **kwargs)
        try:
            if self.reassign is not None:
                if self.doc is not None:
                    self.doc += f", reassign: {self.reassign}"
                else:
                    self.doc = f"reassign: {self.reassign}"
        except KeyError as ke:
            pass
    
    def pre_set(self, obj, value):
        if id(obj) not in self.__dict__:
            self.__dict__[id(obj)] = 0
        if self.number_of_assignment is None:
            self.number_of_assignment = 0
            
        return super().pre_set(obj, value)
        
    def post_set(self, obj, value):
        if id(obj) in self.__dict__:
            self.__dict__[id(obj)] += 1
            self.number_of_assignment += 1
            
        return super(ReassignValidator, self).post_set(obj=obj, value=value)

    def validate(self, instance=None, value=None):
        self._validate_reassignment(instance=instance, value=value)

    def _validate_reassignment(self, instance, value):  # noqa
        reassign = None
        try:
            reassign = self.reassign
        except KeyError as ke:
            pass 
        
        if reassign is not None and not reassign:
            if logger := self.logger:
                logger.info(f"{self.name}: Reassign: {reassign}")
                
            if id(instance) in self.__dict__ and self.__dict__[id(instance)] >= 1:
                raise AttributeError(
                    f"{self.name} can be assignend only once, "
                    f"attempted to reassign with value '{value}' instead"
                )


@dataclass
class MultipleValidator(ValidateProperty):
    multiple_of: VALUE = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            multiple_of: VALUE = None,
            debug: DEBUG = None,
            doc: DOC = None,
            name: NAME = None,
            **kwargs
    ):  
        self.multiple_of = multiple_of
        super(MultipleValidator, self).__init__(debug=debug, doc=doc, name=name, **kwargs)
        try:
            if self.multiple_of is not None:
                if self.doc is not None:
                    self.doc += f", multiple_of: {self.multiple_of!r}"
                else:
                    self.doc = f"multiple_of: {self.multiple_of!r}"
        except KeyError as ke:
            pass
        
    def validate(self, instance=None, value=None):
        self._validate_multiple_of(instance=instance, value=value)

    def _validate_multiple_of(self, instance, value):
        multiple_of = None
        try:
            multiple_of = self.multiple_of
        except KeyError as ke:
            pass
        
        if multiple_of is not None and multiple_of:
            if logger := self.logger:
                logger.info(f"{self.name}: Multiple of :{multiple_of}")

            if value is not None:
                if not (value//self.multiple_of) == 0:
                    raise ValueError(
                        f"{self.name} "
                        f"expect the value multiple of {multiple_of}, "
                        f"got {value} instead"
                    )


@dataclass
class MinValueValidator(ValidateProperty):
    min_value: VALUE = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            min_value: VALUE = None,
            gt: VALUE = None,
            debug: DEBUG = None,
            doc: DOC = None,
            name: NAME = None,
            **kwargs,
    ):
        if all([min_value, gt]):
            raise ValueError("min_value and gt both can't be initialized, select one")
        
        self.min_value = min_value or gt
        
        super(MinValueValidator, self).__init__(debug=debug, doc=doc, name=name, **kwargs)
        try:
            if self.min_value is not None:
                if self.doc is not None:
                    self.doc += f", min_value: {self.min_value!r}"
                else:
                    self.doc = f"min_value: {self.min_value!r}"
        except KeyError as ke:
            pass
        
    def validate(self, instance=None, value=None):
        self._validate_min_value(instance, value)

    def _validate_min_value(self, instance, value):
        min_value = None
        try:
            if self.min_value is not None and self.min_value:
                min_value = self.min_value
        except KeyError as ke:
            pass
        
        if min_value is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: MinValue: min_value = {min_value}")
            
            if value is not None:
                if value < min_value:
                    raise ValueError(
                        f"{self.name} "
                        f"expect the minimum value of {min_value}, "
                        f"got {value} instead"
                    )


@dataclass
class MaxValueValidator(ValidateProperty):
    max_value: VALUE = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            max_value: VALUE = None,
            lt: VALUE = None,
            debug: DEBUG = None,
            doc: DOC = None,
            name: NAME = None,
            **kwargs,
    ):

        if all([max_value, lt]):
            raise ValueError(f"max_value and lt both can't be initialized, select one")
        
        self.max_value = max_value or lt

        super(MaxValueValidator, self).__init__(debug=debug, doc=doc, name=name, **kwargs)
        try:
            if self.max_value is not None:
                if self.doc is not None:
                    self.doc += f", max_value: {self.max_value!r}"
                else:
                    self.doc = f"max_value: {self.max_value!r}"
        except KeyError as ke:
            pass
        
    def validate(self, instance=None, value=None):
        self._validate_max_value(instance, value)

    def _validate_max_value(self, instance, value):  # noqa
        max_value = None
        try:
            if self.max_value is not None and self.max_value:
                max_value = self.max_value
        except KeyError as ke:
            pass
        
        if max_value is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: MaxValue: " f"max_value = {max_value}")
        
            if value is not None:
                if value > max_value:
                    raise ValueError(
                        f"{self.name} "
                        f"expect the maximum value of {max_value}, "
                        f"got {value} instead"
                    )


@dataclass
class ValueValidator(MinValueValidator, MaxValueValidator):
    value: VALUE = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            min_value: VALUE = None,
            gt: VALUE = None,
            value: VALUE = None,
            eq: VALUE = None,
            max_value: VALUE = None,
            lt: VALUE = None,
            debug: DEBUG = None,
            doc: DOC = None,
            name: NAME = None,
            **kwargs,
    ):
        if all([max_value, lt]):
            raise ValueError(f"max_value and lt both can't be initialized, select one")

        if all([min_value, gt]):
            raise ValueError("min_value and gt both can't be initialized, select one")

        if all([value, eq]):
            raise ValueError("value and eq both can't be initialized, select one")

        max_value = max_value or lt
        min_value = min_value or gt
        value = value or eq

        if min_value is not None and max_value is not None:
            if max_value < min_value:  # type: ignore
                raise ValueError(f"{'max_value' if lt is None else 'lt'} can not be less than "
                                 f"{'min_value' if gt is None else 'gt'}")

        if min_value is not None and value is not None:
            if value < min_value:  # type: ignore
                raise ValueError(f"{'value' if eq is None else 'eq'} can not be less than "
                                 f"{'min_value' if gt is None else 'gt'}")

        if max_value is not None or value is not None:
            if max_value < value:  # type: ignore
                raise ValueError(f"{'value' if eq is None else 'eq'} can not be more than "
                                 f"{'max_value' if lt is None else 'lt'}")
        self.value = value

        super(ValueValidator, self).__init__(
            min_value=min_value,
            max_value=max_value,
            debug=debug,
            doc=doc,
            name=name,
            **kwargs,
        )
        try:
            if self.value is not None:
                if self.doc is not None:
                    self.doc += f", value: {self.value!r}"
                else:
                    self.doc = f"value: {self.value!r}"
        except KeyError as ke:
            pass
        
    def validate(self, instance=None, value=None):
        self._validate_value(instance, value)

    def _validate_value(self, instance, value):
        self._validate_min_value(instance, value)
        self._validate_max_value(instance, value)
        of_value = None
        try:
            if self.value is not None and self.value:
                of_value = self.value
        except KeyError as ke:
            pass
        if of_value is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: Value: " f"value = {self.value}")

            if value is not None:
                if value != of_value:
                    raise ValueError(
                        f"{self.name} "
                        f"expect the value {of_value}, "
                        f"got {value} as value instead"
                    )


@dataclass
class MinLengthValidator(ValidateProperty):
    min_length: INT = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            min_length: INT = None,
            debug: DEBUG = None,
            doc: DOC = None,
            name: NAME = None,
            **kwargs,
    ):
        self.min_length = min_length
        super(MinLengthValidator, self).__init__(debug=debug, doc=doc, name=name, **kwargs)
        try:
            if self.min_length is not None:
                if self.doc is not None:
                    self.doc += f", min_length: {self.min_length}"
                else:
                    self.doc = f"min_length: {self.min_length}"
        except KeyError as ke:
            pass 
        
    def validate(self, instance=None, value=None):
        self._validate_min_length(instance, value)

    def _validate_min_length(self, instance, value):  # noqa
        min_length = None
        try:
            if self.min_length is not None and self.min_length:
                min_length = self.min_length
        except KeyError as ke:
            pass 
        
        if min_length is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: MinLength: " f"min_length = {min_length}")

            if value is not None:
                value_length = len(value)
                if value_length < min_length:
                    raise ValueError(
                        f"{self.name} "
                        f"expect the value of minimum length {min_length}, "
                        f"got length {value_length} value instead"
                    )


@dataclass
class MaxLengthValidator(ValidateProperty):
    max_length: INT = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            max_length: INT = None,
            debug: DEBUG = None,
            doc: DOC = None,
            name: NAME = None,
            **kwargs,
    ):
        self.max_length = max_length

        super(MaxLengthValidator, self).__init__(debug=debug, doc=doc, name=name, **kwargs)
        try:
            if self.max_length is not None:
                if self.doc is not None:
                    self.doc += f", max_length: {self.max_length}"
                else:
                    self.doc = f"max_length: {self.max_length}"
        except KeyError as ke:
            pass

    def validate(self, instance=None, value=None):
        self._validate_max_length(instance, value)

    def _validate_max_length(self, instance, value):  # noqa
        max_length = None 
        try:
            if self.max_length is not None and self.max_length:
                max_length = self.max_length
        except KeyError as ke:
            pass 
        
        if max_length is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: MaxLength: " f"max_length = {max_length}")

            if value is not None:
                value_length = len(value)
                if value_length > max_length:
                    raise ValueError(
                        f"{self.name} "
                        f"expect the value of maximum length {max_length}, "
                        f"got length {value_length} value instead"
                    )


@dataclass
class LengthValidator(MinLengthValidator, MaxLengthValidator):
    length: INT = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            min_length: INT = None,
            length: INT = None,
            max_length: INT = None,
            debug: DEBUG = None,
            doc: DOC = None,
            name: NAME = None,
            **kwargs,
    ):
        if min_length is not None and max_length is not None:
            if max_length < min_length:  # type: ignore
                raise ValueError(f"max_length can not be less than min_length")

        if min_length is not None and length is not None:
            if length < min_length:  # type: ignore
                raise ValueError(f"length can not be less than min_length")

        if max_length is not None and length is not None:
            if max_length < length:  # type: ignore
                raise ValueError(f"length can not be more than max_length")
        
        self.length = length
        
        super(LengthValidator, self).__init__(
            min_length=min_length,
            max_length=max_length,
            debug=debug,
            doc=doc,
            name=name,
            **kwargs,
        )
        try:
            if self.length is not None:
                if self.doc is not None:
                    self.doc += f", length: {self.length}"
                else:
                    self.doc = f"length: {self.length}"
        except KeyError as ke:
            pass 
        
    def validate(self, instance=None, value=None):
        self._validate_length(instance, value)

    def _validate_length(self, instance, value):
        self._validate_min_length(instance=instance, value=value)
        self._validate_max_length(instance=instance, value=value)
        
        length = None 
        
        try:
            if self.length is not None and self.length:
                length = self.length
        except KeyError as ke:
            pass 
        
        if length is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: Length: " f"length = {length}")

            if value is not None:
                value_length = len(value)
                if value_length != length:
                        raise ValueError(
                            f"{self.name} "
                            f"expect the value of length {length}, "
                            f"got length {value_length} value instead"
                        )


@dataclass
class ExpiryValidator(ValidateProperty):
    expiry: DATE_TIME_DELTA = TypeValidator(logger=False, debug=True)
    timeline: STR = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs,
    ):
        dates = eu_date | ind_date
        date_pattern = PatternValidator(pattern=dates, debug=debug, name="expiry")
        reassign_date = ReassignValidator(reassign=False, debug=debug, name="expiry")
        reassign_timeline = ReassignValidator(reassign=False, debug=debug, name="timeline")
        if not any([expire_before, expire_on, expire_before]):
            self.expiry = None
            self.timeline = None
            
        if expire_after is not None:
            reassign_date.validate(value=expire_after)
            if isinstance(expire_after, str):
                date_pattern.validate(value=expire_after)
            self.expiry = expire_after

            reassign_timeline.validate(value="after")
            self.timeline = "after"

        if expire_on is not None:
            reassign_date.validate(value=expire_on)
            if isinstance(expire_on, str):
                date_pattern.validate(value=expire_on)
            self.expiry = expire_on

            reassign_timeline.validate(value="on")
            self.timeline = "on"

        if expire_before is not None:
            reassign_date.validate(value=expire_before)
            if isinstance(expire_after, str):
                date_pattern.validate(value=expire_before)
            self.expiry = expire_before

            reassign_timeline.validate(value="before")
            self.timeline = "before"
        
        super(ExpiryValidator, self).__init__(debug=debug, doc=doc, **kwargs)
        try:
            if self.expiry is not None:
                if self.doc is not None:
                    self.doc += f", expiry_{self.timeline}: {self.expiry}"
                else:
                    self.doc = f"expiry_{self.timeline}: {self.expiry}"
        except KeyError as ke:
            pass 
        
    def validate(self, instance=None, value=None):
        self._validate_expiry(instance, value)

    def _validate_expiry(self, instance, value):  # noqa
        expiry = None
        try:
            if self.expiry is not None and self.expiry:
                expiry = self.expiry
        except KeyError as ke:
            pass
        
        if expiry is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: Timer: expiry {self.timeline} = {expiry}")

            if value is not None:
                if isinstance(expiry, str):
                    try:
                        expiry = list(get_date(expiry))[0]["datetime"]
                        if not isinstance(expiry, datetime.datetime):
                            raise TypeError(
                                f"something went wrong, "
                                f"expect expiry to be a {datetime.datetime.__name__} type, "
                                f"got {type(expiry).__name__} type instead"
                            )
                        now = datetime.datetime.now(tz=expiry.tzinfo)

                    except (TypeError, ValueError, AttributeError, Exception):
                        msg = f"{self.name} expiry must have the pattern 'YYYY-MM-DD'"
                        raise ValueError(msg)

                elif isinstance(expiry, datetime.datetime):
                    now = datetime.datetime.now(tz=expiry.tzinfo)
                elif isinstance(expiry, datetime.date):
                    expiry = datetime.datetime.combine(expiry, datetime.time.min)
                    now = datetime.datetime.now(tz=expiry.tzinfo)
                elif isinstance(expiry, datetime.time):
                    expiry = datetime.datetime.combine(datetime.date.today(), expiry)
                    now = datetime.datetime.now(tz=expiry.tzinfo)
                else:
                    msg = f"{self.name} expiry must have the pattern 'YYYY-MM-DD'"
                    raise ValueError(msg)

                if self.timeline == "after":
                    cond = now > expiry
                elif self.timeline == "on":
                    cond = now == expiry
                elif self.timeline == "before":
                    cond = now < expiry
                else:
                    msg = "expiry condition not yet found"
                    raise ValueError(msg)
                if cond:
                    msg = f"{self.name} expired {self.timeline} {self.expiry}"
                    raise ValueError(msg)


class ChoiceValidator(ValidateProperty):
    in_choice: CHOICE = None
    not_in_choice: CHOICE = None

    def __init__(
            self,
            in_choice: CHOICE = None,
            not_in_choice: CHOICE = None,
            doc: DOC = None,
            debug: BOOL = None,
            **kwargs
    ):
        self.in_choice = in_choice
        self.not_in_choice = not_in_choice
            
        super(ChoiceValidator, self).__init__(
            doc=doc,
            debug=debug,
            **kwargs
        )
        
        try:
            if self.in_choice is not None:
                if self.doc is not None:
                    self.doc += f", in_choice: {self.in_choice}"
                else:
                    self.doc = f"in_choice: {self.in_choice}"
        except KeyError as ke:
            pass  
        
        try:
            if self.not_in_choice is not None:
                if self.doc is not None:
                    self.doc += f", not_in_choice: {self.not_in_choice}"
                else:
                    self.doc = f"not_in_choice: {self.not_in_choice}"
        except KeyError as ke:
            pass 
        
    def validate(self, instance=None, value=None):
        self._validate_choice(instance, value)

    def _validate_choice(self, instance, value):
        self._validate_in_choice(instance, value)
        self._validate_not_in_choice(instance, value)

    def _validate_in_choice(self, instance, value):
        in_choice = None 
        try:
            if self.in_choice is not None and self.in_choice:
                in_choice = self.in_choice
        except KeyError as ke:
            pass
        
        if in_choice is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: In-Choice: {in_choice}")

            if value is not None:
                if value not in in_choice:
                    raise ValueError(
                        f"{self.name} expect values in {in_choice}, "
                        f"got {value} as value instead"
                    )

    def _validate_not_in_choice(self, instance, value):
        not_in_choice = None 
        try:
            if self.not_in_choice is not None and self.not_in_choice:
                not_in_choice = self.not_in_choice
        except KeyError as ke:
            pass
        
        if not_in_choice is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: Not-In-Choice: {not_in_choice}")

            if value in not_in_choice:
                raise ValueError(
                    f"{self.name} does not expect values in {not_in_choice}, "
                    f"got {value} as value instead"
                )


@dataclass
class AttributeValidator(ValidateProperty):
    has_attributes: Union[list[STR], TypeValidator] = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            has_attributes: list[STR] = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs,
    ):
        self.has_attributes = has_attributes
        super(AttributeValidator, self).__init__(doc=doc, debug=debug, **kwargs)
        try:
            if self.has_attributes is not None:
                if self.doc is not None:
                    self.doc += f", has_attributes={self.has_attributes}"
                else:
                    self.doc = f"has_attributes={self.has_attributes}"
        except KeyError as ke:
            pass 
        
    def validate(self, instance=None, value=None):
        self._validate_attribute(instance=instance, value=value)

    def _validate_attribute(self, instance, value):
        has_attributes = None 
        try:
            if self.has_attributes is not None and self.has_attributes:
                has_attributes = self.has_attributes
        except KeyError as ke:
            pass
        
        if has_attributes is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: Has Attributes: {has_attributes}")

            if value is not None:
                for attr in has_attributes:
                    if not hasattr(value, attr):
                        raise AttributeError(f"{self.name} must have an attribute "
                                             f"'{has_attributes}'")


@dataclass
class TaskValidator(ValidateProperty):
    task_interval: INT = TypeValidator(logger=False, debug=True)
    cache_task: BOOL = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            task_interval: INT,
            cache_task: BOOL = True,
            **kwargs
    ):
        self.task_interval = task_interval
        self._pre_validate_tasks: typing.DefaultDict = defaultdict(list)
        self._post_validate_tasks: typing.DefaultDict = defaultdict(list)
        self._post_set_tasks: typing.DefaultDict = defaultdict(list)
        self._pre_get_tasks: typing.DefaultDict = defaultdict(list)
        self._post_get_tasks: typing.DefaultDict = defaultdict(list)
        self._pre_delete_tasks: typing.DefaultDict = defaultdict(list)
        self._post_delete_tasks: typing.DefaultDict = defaultdict(list)
        self.cache_task = cache_task
        self.task: dict = dict()
        self.ok = True
        super(TaskValidator, self).__init__(**kwargs)

    async def _job(self, instance, value, tasks):
        try:
            while self.ok:
                if self.task_interval:
                    await asyncio.sleep(self.task_interval)
                if self.cache_task:
                    if getattr(self.task, tasks, None) is None:
                        self.task[tasks] = [await asyncio.create_task(Cor(instance, value))
                                            for Cor in tasks[instance.__class__.__name__]]

                    return self.task[tasks]
                else:
                    return [await asyncio.create_task(Cor(instance, value))
                            for Cor in tasks[instance.__class__.__name__]]

        except Exception as ex:
            self.cancel(tasks=tasks)
            raise ex

    def cancel(self, tasks):
        self.ok = False
        self.task[tasks] = None

    def validate(self, instance=None, value=None):
        pass

    def add_pre_validator_task(self, func, namespace=None):
        self._pre_validate_tasks[namespace or str(func.__qualname__).split(".")[0]] \
            .append(func if asyncio.iscoroutinefunction(func) else async_wrap(func))
        return func

    def add_post_validator_task(self, func, namespace=None):
        self._post_validate_tasks[namespace or str(func.__qualname__).split(".")[0]] \
            .append(func if asyncio.iscoroutinefunction(func) else async_wrap(func))
        return func

    def add_post_set_task(self, func, namespace=None):
        self._post_set_tasks[namespace or str(func.__qualname__).split(".")[0]] \
            .append(func if asyncio.iscoroutinefunction(func) else async_wrap(func))
        return func

    def add_pre_get_task(self, func, namespace=None):
        self._pre_get_tasks[namespace or str(func.__qualname__).split(".")[0]] \
            .append(func if asyncio.iscoroutinefunction(func) else async_wrap(func))
        return func

    def add_post_get_task(self, func, namespace=None):
        self._post_get_tasks[namespace or str(func.__qualname__).split(".")[0]] \
            .append(func if asyncio.iscoroutinefunction(func) else async_wrap(func))
        return func

    def add_pre_delete_task(self, func, namespace=None):
        self._pre_delete_tasks[namespace or str(func.__qualname__).split(".")[0]] \
            .append(func if asyncio.iscoroutinefunction(func) else async_wrap(func))
        return func

    def add_post_delete_task(self, func, namespace=None):
        self._post_delete_tasks[namespace or str(func.__qualname__).split(".")[0]] \
            .append(func if asyncio.iscoroutinefunction(func) else async_wrap(func))
        return func

    def pre_validation_processing(self, instance, value):
        asyncio.run(main(self._job(instance=instance, value=value, tasks=self._pre_validate_tasks)))
        super(TaskValidator, self).pre_validation_processing(instance=instance, value=value)

    def post_validation_processing(self, instance, value):
        asyncio.run(main(self._job(instance=instance, value=value, tasks=self._post_validate_tasks)))
        super(TaskValidator, self).post_validation_processing(instance=instance, value=value)

    def post_set_processing(self, instance, value):
        asyncio.run(main(self._job(instance=instance, value=value, tasks=self._post_set_tasks)))
        super(TaskValidator, self).post_set_processing(instance=instance, value=value)

    def pre_get_processing(self, instance, value):
        asyncio.run(main(self._job(instance=instance, value=value, tasks=self._pre_get_tasks)))
        super(TaskValidator, self).pre_get_processing(instance=instance, value=value)

    def post_get_processing(self, instance, value):
        asyncio.run(main(self._job(instance=instance, value=value, tasks=self._post_get_tasks)))
        super(TaskValidator, self).post_get_processing(instance=instance, value=value)

    def pre_delete_processing(self, instance, value):
        asyncio.run(main(self._job(instance=instance, value=value, tasks=self._pre_delete_tasks)))
        super(TaskValidator, self).pre_delete_processing(instance=instance, value=value)

    def post_delete_processing(self, instance, value):
        asyncio.run(main(self._job(instance=instance, value=value, tasks=self._post_delete_tasks)))
        super(TaskValidator, self).post_delete_processing(instance=instance, value=value)


@dataclass
class Validator(
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
    TaskValidator
):
    """Validator: base class for validation of different Properties.

    Usage:

    >>> from dataclasses import dataclass
    >>> @dataclass
    ... class Accounts(object):
    ...     username: str = Validator(
    ...         required=True,
    ...         reassign=False,
    ...         min_length=3,
    ...         default="Ajay Kumar",
    ...         min_value="A",
    ...         expire_before="2020-08-14",
    ...     )
    ...     password: str = Validator(reassign=False, min_length=3, default="sks")
    """

    enable_async: BOOL = TypeValidator(logger=False, debug=True)
    allow_validation: BOOL = TypeValidator(logger=False, debug=True)
    # cache_validation: BOOL = TypeValidator(logger=False, debug=True)
    default: DEFAULT = None
    
    def __init__(
            self,
            default: DEFAULT = None,
            name: NAME = None,
            doc: DOC = None,
            required: BOOL = None,
            pattern: PATTERN = None,
            reassign: BOOL = None,
            multiple_of: VALUE = None,
            min_value: VALUE = None,
            value: VALUE = None,
            max_value: VALUE = None,
            gt: VALUE = None,
            eq: VALUE = None,
            lt: VALUE = None,
            min_length: INT = None,
            length: INT = None,
            max_length: INT = None,
            expire_after: DATE_TIME_DELTA = None,
            expire_on: DATE_TIME_DELTA = None,
            expire_before: DATE_TIME_DELTA = None,
            in_choice: CHOICE = None,
            not_in_choice: CHOICE = None,
            has_attributes: list[STR] = None,
            task_interval: INT = None,
            cache_task: BOOL = True,
            debug: DEBUG = None,
            # cache_validation: BOOL = None,
            enable_async: BOOL = None,
            allow_validation: BOOL = True,
            **kwargs,
    ):

        super(Validator, self).__init__(
            default=default,
            name=name,
            doc=doc,
            required=required,
            pattern=pattern,
            reassign=reassign,
            multiple_of=multiple_of,
            min_value=min_value,
            value=value,
            max_value=max_value,
            gt=gt,
            eq=eq,
            lt=lt,
            min_length=min_length,
            length=length,
            max_length=max_length,
            expire_after=expire_after,
            expire_on=expire_on,
            expire_before=expire_before,
            in_choice=in_choice,
            not_in_choice=not_in_choice,
            has_attributes=has_attributes,
            task_interval=task_interval,
            cache_task=cache_task,
            debug=debug,
            **kwargs,
        )
        self._dict = None
        self.enable_async = enable_async  # type: ignore  # noqa
        self._custom_validators: typing.DefaultDict = defaultdict(list)
        self._custom_pre_validator: typing.DefaultDict = defaultdict(list)
        self._custom_post_validator: typing.DefaultDict = defaultdict(list)
        self._custom_post_set_processor: typing.DefaultDict = defaultdict(list)
        self._custom_pre_get_processor: typing.DefaultDict = defaultdict(list)
        self._custom_post_get_processor: typing.DefaultDict = defaultdict(list)
        self._custom_pre_delete_processor: typing.DefaultDict = defaultdict(list)
        self._custom_post_delete_processor: typing.DefaultDict = defaultdict(list)
        self.allow_validation = allow_validation
        # self.cache_validation = cache_validation

        # if self.cache_validation:
        #     self._validate_field = timed_lru_cache(seconds=30, maxsize=128)(self._validate_field)
        #     self._async_validate_field = timed_lru_cache(seconds=30, maxsize=128)(self._async_validate_field)


    def validate(self, instance=None, value=None):
        if self.allow_validation is not None and self.allow_validation:
            if not self.enable_async:
                self._validate_field(instance, value)
            else:
                self._async_validate_field(instance, value)

    def _validate_field(self, instance, value):
        """
        :param value: any type of values are accepted to be validated here
        to be validated synchronously.
        :return: if value is not validated, this method raises errors
        """
        _validators = [
            self._validate_reassignment(instance, value),
            self._validate_type(instance, value),
            self._validate_required(instance, value),
            self._validate_pattern(instance, value),
            self._validate_multiple_of(instance, value),
            self._validate_length(instance, value),
            self._validate_value(instance, value),
            self._validate_expiry(instance, value),
            self._validate_choice(instance, value),
            self._validate_attribute(instance, value)
        ]
        for func in self._custom_validators[instance.__class__.__name__]:
            if asyncio.iscoroutinefunction(func):
                _validators.extend(asyncio.get_event_loop().run_until_complete(func(instance, value)))
            else:
                _validators.append(func(instance, value))
        return _validators

    def _async_validate_field(self, instance, value):
        _validators = [
            async_wrap(self._validate_reassignment)(instance, value),
            async_wrap(self._validate_type)(instance, value),
            async_wrap(self._validate_required)(instance, value),
            async_wrap(self._validate_pattern)(instance, value),
            async_wrap(self._validate_multiple_of)(instance, value),
            async_wrap(self._validate_length)(instance, value),
            async_wrap(self._validate_value)(instance, value),
            async_wrap(self._validate_expiry)(instance, value),
            async_wrap(self._validate_choice)(instance, value),
            async_wrap(self._validate_attribute)(instance, value)
        ]

        _validators += [
            async_wrap(func)(instance, value)
            if not asyncio.iscoroutinefunction(func)
            else func(instance, value)
            for func in self._custom_validators[instance.__class__.__name__]
        ]
        return asyncio.run(main(*_validators))

    def add_validator(self, func, namespace=None):
        """custom validator functions and methods are accepted here
        and validated"""
        func_class_name = namespace or str(func.__qualname__).split(".")[0]
        self._custom_validators[func_class_name].append(func)
        return func
    
    def _processing(self, func_default_dict, task_default_dict, instance, value):
        for func in func_default_dict[instance.__class__.__name__]:
            if self.enable_async:
                if not asyncio.iscoroutinefunction(func):
                    cor = async_wrap(func)(instance, value)
                else:
                    cor = func(instance, value)
                value = asyncio.run(main(cor))[0]
            else:
                value = func(instance, value)
                if asyncio.iscoroutine(value):
                    value = asyncio.run(main(value))[0]

        if any(task_default_dict):
            asyncio.run(main(self._job(instance=instance, value=value, tasks=task_default_dict)))

        return value

    def pre_validation_processing(self, instance, value):
        return self._processing(
            func_default_dict=self._custom_pre_validator, 
            task_default_dict=self._pre_validate_tasks, 
            instance=instance, 
            value=value
            )

    def add_pre_validator(self, func, namespace=None):
        func_class_name = namespace or str(func.__qualname__).split(".")[0]
        self._custom_pre_validator[func_class_name].append(func)
        return func

    def post_validation_processing(self, instance, value):
        return self._processing(
            func_default_dict=self._custom_post_validator, 
            task_default_dict=self._post_validate_tasks, 
            instance=instance, 
            value=value
            )

    def add_post_validator(self, func, namespace=None):
        func_class_name = namespace or str(func.__qualname__).split(".")[0]
        self._custom_post_validator[func_class_name].append(func)
        return func

    def post_set_processing(self, instance, value):
        return self._processing(
            func_default_dict=self._custom_post_set_processor, 
            task_default_dict=self._post_set_tasks, 
            instance=instance, 
            value=value
            )
        
    def add_post_set(self, func, namespace=None):
        func_class_name = namespace or str(func.__qualname__).split(".")[0]
        self._custom_post_set_processor[func_class_name].append(func)
        return func

    def pre_get_processing(self, instance, value):
        return self._processing(
            func_default_dict=self._custom_pre_get_processor, 
            task_default_dict=self._pre_get_tasks, 
            instance=instance, 
            value=value
            )
        
    def add_pre_get(self, func, namespace=None):
        func_class_name = namespace or str(func.__qualname__).split(".")[0]
        self._custom_pre_get_processor[func_class_name].append(func)
        return func

    def post_get_processing(self, instance, value):
        return self._processing(
            func_default_dict=self._custom_post_get_processor, 
            task_default_dict=self._post_get_tasks, 
            instance=instance, 
            value=value
            )

    def add_post_get(self, func, namespace=None):
        func_class_name = namespace or str(func.__qualname__).split(".")[0]
        self._custom_post_get_processor[func_class_name].append(func)
        return func

    def pre_delete_processing(self, instance, value):
        return self._processing(
            func_default_dict=self._custom_pre_delete_processor, 
            task_default_dict=self._pre_delete_tasks, 
            instance=instance, 
            value=value
            )

    def add_pre_delete(self, func, namespace=None):
        func_class_name = namespace or str(func.__qualname__).split(".")[0]
        self._custom_pre_delete_processor[func_class_name].append(func)
        return func

    def post_delete_processing(self, instance, value):
        return self._processing(
            func_default_dict=self._custom_post_delete_processor, 
            task_default_dict=self._post_delete_tasks, 
            instance=instance, 
            value=value
            )

    def add_post_delete(self, func, namespace=None):
        func_class_name = namespace or str(func.__qualname__).split(".")[0]
        self._custom_post_delete_processor[func_class_name].append(func)
        return func


def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        p_func = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, p_func)

    return run


async def main(*args):
    return await asyncio.gather(*args)


class IntegerValidator(Validator):
    multiple_of: INT = TypeValidator(logger=False, debug=True)
    min_value: INT = TypeValidator(logger=False, debug=True)
    value: INT = TypeValidator(logger=False, debug=True)
    max_value: INT = TypeValidator(logger=False, debug=True)
    annotation = INT


class FloatValidator(Validator):
    multiple_of: FLOAT = TypeValidator(logger=False, debug=True)
    min_value: FLOAT = TypeValidator(logger=False, debug=True)
    value: FLOAT = TypeValidator(logger=False, debug=True)
    max_value: FLOAT = TypeValidator(logger=False, debug=True)
    annotation = FLOAT


class DecimalValidator(Validator):
    multiple_of: DECIMAL = TypeValidator(logger=False, debug=True)
    min_value: DECIMAL = TypeValidator(logger=False, debug=True)
    value: DEBUG = TypeValidator(logger=False, debug=True)
    max_value: DECIMAL = TypeValidator(logger=False, debug=True)
    annotation = DECIMAL


class BooleanValidator(Validator):
    annotation = BOOL


class BytesValidator(Validator):
    min_value: BYTES = TypeValidator(logger=False, debug=True)
    value: BYTES = TypeValidator(logger=False, debug=True)
    max_value: BYTES = TypeValidator(logger=False, debug=True)
    annotation = BYTES


class StringValidator(Validator):
    min_value: STR = TypeValidator(logger=False, debug=True)
    value: STR = TypeValidator(logger=False, debug=True)
    max_value: STR = TypeValidator(logger=False, debug=True)
    annotation = STR

    def _validate_min_value(self, instance, value):
        min_value = None
        try:
            if self.min_value is not None and self.min_value:
                min_value= self.min_value
        except KeyError as ke:
            pass 
        
        if min_value is not None:
            if logger := self.logger:
                logger.info(
                    f"{self.name}: MinValue: 'min_value = {min_value}'"
                )
            if value is not None:
                if value < min_value:
                    raise ValueError(
                        f"{self.name} "
                        f"expect the start of string with {min_value} or above, "
                        f"got {value} as value instead"
                    ) from None

class HexShortColorValidator(StringValidator):

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_hex_short_color_pattern,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(HexShortColorValidator, self).validate(instance=instance, value=value)

    def _validate_hex_short_color_pattern(self, instance, value):
        if not re.compile(relib.r_hex_short.pattern, re.IGNORECASE).fullmatch(value):
            raise ValueError(f"{self.name} got an invalid hex short color {value}") from None
 
 
class HexLongColorValidator(StringValidator):

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_hex_long_color_pattern,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(HexLongColorValidator, self).validate(instance=instance, value=value)

    def _validate_hex_long_color_pattern(self, instance, value):
        if not re.compile(relib.r_hex_long.pattern, re.IGNORECASE).fullmatch(value):
            raise ValueError(f"{self.name} got an invalid hex long color {value}") from None
 

class HexColorValidator(StringValidator):

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_hex_short_or_hex_long_color_pattern,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(HexColorValidator, self).validate(instance=instance, value=value)

    def _validate_hex_short_or_hex_long_color_pattern(self, instance, value):
        if not re.compile((relib.r_hex_long | relib.r_hex_short).pattern, re.IGNORECASE).fullmatch(value):
            raise ValueError(f"{self.name} got an invalid hex (short or long) color {value}") from None
        

class RGBOrRGBAColorValidator(StringValidator):

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_rgb_or_rgba_color_pattern,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(RGBOrRGBAColorValidator, self).validate(instance=instance, value=value)

    def _validate_rgb_or_rgba_color_pattern(self, instance, value):
        if not re.compile((relib.r_rgb | relib.r_rbga).pattern, re.IGNORECASE).fullmatch(value):
            raise ValueError(f"{self.name} got an invalid rgb or rbga color {value}") from None



class HSLOrHSLAColorValidator(StringValidator):

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_hsl_or_hsla_color_pattern,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(HSLOrHSLAColorValidator, self).validate(instance=instance, value=value)

    def _validate_hsl_or_hsla_color_pattern(self, instance, value):
        if not re.compile((relib.r_rgb | relib.r_rbga).pattern, re.IGNORECASE).fullmatch(value):
            raise ValueError(f"{self.name} got an invalid hsl or hsla color {value}") from None



class DateValidator(Validator):
    hyphen = regexps.Pattern(r"-", alias="-")
    colon = regexps.Pattern(r":", alias=":")
    backslash = regexps.Pattern(r"/", alias="/")
    yyyy = regexps.WordBoundary(regexps.Pattern(r"\d", count=4, alias="YYYY"))
    mm = regexps.WordBoundary(regexps.Pattern(months_numbers.pattern, alias="MM"))
    dd = regexps.WordBoundary(regexps.Pattern(day_numbers.pattern, alias="DD"))

    eu_date_with_hyphen = yyyy & hyphen & mm & hyphen & dd
    eu_date_with_colon = yyyy & colon & mm & colon & dd
    eu_date_with_backslash = yyyy & backslash & mm & backslash & dd
    eu_date = eu_date_with_colon | eu_date_with_hyphen | eu_date_with_backslash

    ind_date_with_hyphen = dd & hyphen & mm & hyphen & yyyy
    ind_date_with_colon = dd & colon & mm & colon & yyyy
    ind_date_with_backslash = dd & backslash & mm & backslash & yyyy
    ind_date = ind_date_with_colon | ind_date_with_hyphen | ind_date_with_backslash

    min_value: DATE_TIME_DELTA = TypeValidator(logger=False, debug=True)
    value: DATE_TIME_DELTA = TypeValidator(logger=False, debug=True)
    max_value: DATE_TIME_DELTA = TypeValidator(logger=False, debug=True)
    annotation = DATE_TIME_DELTA

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs,
    ):

        super(DateValidator, self).__init__(
            default=default,
            required=required,
            reassign=reassign,
            pattern=self.eu_date | self.ind_date,
            name=name,
            doc=doc,
            debug=debug,
            **kwargs,
        )

    def _validate_pattern(self, instance, value):  # noqa
        if self.pattern is not None:
            pattern = (
                self.pattern.pattern
                if isinstance(self.pattern, regexps.PatternType)
                else self.pattern
            )
            if logger := self.logger:
                logger.info(f"{self.name}: Regexp: {self.pattern}")

            value = value if isinstance(value, str) else None
            if value is not None:
                get_pattern = re.compile(pattern).findall
                pattern = get_pattern(value)
                if not any(pattern):
                    raise ValueError(
                        f"{self.name}: must have the pattern {self.pattern.alias}, got {value} instead"
                    ) from None


class EnumValidator(Validator):
    annotation = ENUM


class StringEnumValidator(Validator):
    annotation = STR_ENUM


class IntegerEnumValidator(Validator):
    annotation = INT_ENUM


class UUIDValidator(Validator):
    annotation = UUID_Type


@dataclass
class EmailIDValidator(StringValidator):

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs
    ):
        super(EmailIDValidator, self).__init__(
            default=default,
            required=required,
            reassign=reassign,
            pattern=relib.email_pattern,
            name=name,
            doc=doc,
            debug=debug,
            **kwargs,
        )


@dataclass
class PaymentCardValidator(StringValidator):

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs
    ):
        super(PaymentCardValidator, self).__init__(
            default=default,
            required=required,
            reassign=reassign,
            name=name,
            doc=doc,
            debug=debug,
            **kwargs,
        )

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_payment_card,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(PaymentCardValidator, self).validate(instance=instance, value=value)

    def _validate_payment_card(self, instance=None, value=None):  # noqa
        if value is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: PaymentCard")

            if not relib.is_valid_payment_card(value):
                raise ValueError(f"{self.name} is not a valid payment card number") from None


@dataclass
class PhoneNumberValidator(StringValidator):

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs
    ):
        super(PhoneNumberValidator, self).__init__(
            default=default,
            required=required,
            reassign=reassign,
            name=name,
            doc=doc,
            debug=debug,
            **kwargs,
        )

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_phone_number,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(PhoneNumberValidator, self).validate(instance=instance, value=value)

    def _validate_phone_number(self, instance=None, value=None):  # noqa
        if value is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: PhoneNumber")
            region = getattr(instance, "region", "IN") \
                if instance else getattr(self, "region", "IN")
            phone_number = list(phn.PhoneNumberMatcher(value, region=region))
            if not any(phone_number):
                raise ValueError(f"{self.name} is not a valid {region} phone number") \
                    from None

@dataclass
class PathValidator(StringValidator):
    annotation = PATH
    path_exists: BOOL = TypeValidator(logger=False, debug=True)

    def __init__(
            self,
            default=None,
            required: BOOL = None,
            reassign: BOOL = None,
            name: NAME = None,
            doc: DOC = None,
            debug: DEBUG = None,
            path_exists: BOOL = None,
            **kwargs
    ):
        if path_exists is not None:
            self.path_exists = path_exists
        super(PathValidator, self).__init__(
            default=default,
            required=required,
            reassign=reassign,
            name=name,
            doc=doc,
            debug=debug,
            **kwargs,
        )

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_file_path,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(PathValidator, self).validate(instance=instance, value=value)

    def _validate_file_path(self, instance, value):
        if value is not None:
            if isinstance(value, str):
                value = pathlib.Path(value)
            if not (value.is_file() or value.is_dir()):
                raise ValueError(f"{self.name} expects a path, "
                                 f"got {value} instead") from None
            if self.path_exists is not None and self.path_exists:
                if not value.exists():
                    raise FileNotFoundError(f"{self.name} expects an existing file, found None")


class IP4AddressValidator(StringValidator):

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_ip4address,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(IP4AddressValidator, self).validate(instance=instance, value=value)

    def _validate_ip4address(self, instance, value):
        if value is not None:
            try:
                ipaddress.IPv4Address(value)
            except (Exception,):
                raise ValueError(f"{self.name} expects a valid ip4address,"
                                 f" got {value} as value instead") from None


class IP6AddressValidator(StringValidator):

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_ip6address,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(IP6AddressValidator, self).validate(instance=instance, value=value)

    def _validate_ip6address(self, instance, value):
        if value is not None:
            try:
                ipaddress.IPv6Address(value)
            except (Exception,):
                raise ValueError(f"{self.name} expects a valid ip6address,"
                                 f" got {value} as value instead") from None


class IPAnyAddressValidator(StringValidator):

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_ip46address,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(IPAnyAddressValidator, self).validate(instance=instance, value=value)

    def _validate_ip46address(self, instance, value):
        if value is not None:
            try:
                try:
                    ipaddress.IPv4Address(value)
                except (Exception,):
                    ipaddress.IPv6Address(value)
            except (Exception,):
                raise ValueError(f"{self.name} expects a valid ipaddress,"
                                 f" got {value} as value instead")


@dataclass
class AadhaarCardValidator(StringValidator):

    def __init__(
            self,
            required: BOOL = None,
            reassign: BOOL = None,
            name: NAME = None,
            doc: DOC = None,
            **kwargs
    ):
        super(AadhaarCardValidator, self).__init__(
            required=required,
            reassign=reassign,
            name=name,
            doc=doc,
            **kwargs
        )

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_aadhaar_number,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(AadhaarCardValidator, self).validate(instance=instance, value=value)

    def _validate_aadhaar_number(self, instance=None, value=None):  # noqa
        if value is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: AadhaarNumber")

            if not relib.is_valid_aadhaar_card(value):
                raise ValueError(f"{self.name} expects a valid aadhaar number, "
                                 f"{value} is not a valid number") from None


class PANCardValidator(Validator):

    def __init__(
            self,
            required: BOOL = None,
            reassign: BOOL = None,
            name: NAME = None,
            doc: DOC = None,
            **kwargs
    ):
        super(PANCardValidator, self).__init__(
            required=required,
            reassign=reassign,
            name=name,
            doc=doc,
            **kwargs
        )

    def validate(self, instance=None, value=None):
        self.add_validator(self._validate_pan,
                           namespace=instance.__class__.__name__ if instance is not None else None)
        super(PANCardValidator, self).validate(instance=instance, value=value)

    def _validate_pan(self, instance=None, value=None):  # noqa
        if value is not None:
            if logger := self.logger:
                logger.info(f"{self.name}: PAN Card")

            if not relib.is_valid_pan_number(value):
                raise ValueError(f"{self.name} expects a valid PAN Card number, "
                                 f"{value} is not a valid number")


class MappingValidator(Validator):
    annotation = typing.Mapping


class SequenceValidator(Validator):
    annotation = typing.Sequence


class ListValidator(Validator):
    annotation = LIST


class DictionaryValidator(Validator):
    annotation = DICT


class SetValidator(Validator):
    annotation = SET


class TupleValidator(Validator):
    annotation = TUPLE


# if __name__ == "__main__":
#     from cProfile import run
#     from dataclasses import dataclass
#     from datetime import datetime as dt
#     from timeit import timeit

#     @dataclass
#     class LOL(object):
#         xyz: str | Validator | None = Validator(
#             debug=True, 
#             logger=False, 
#             required=True, 
#             expire_after=dt(year=2022, month=7, day=28),   #"28/06/2022", # this  parameter is the costliest in performance
#             reassign=False,
#             in_choice=["Come", "Go", "Stay"],
#             enable_async=True
#             )
#     run('LOL(xyz="Come")')
    # print(timeit('LOL(xyz="Come")', globals=globals(), number=100000))
    # l = LOL(xyz="Come")
    # print(l)
    # w = LOL(xyz="Go")
    # print(w)
    # w.xyz = "1"
    # z = LOL(xyz="Stay")
    # print(z)
    # l.xyz = "Go"
    # print(l)

    # @dataclass
    # class Test(object):
    #     aadhaar_number: typing.Union[str, Validator] = AadhaarCardValidator(logger=False, debug=True)
    #     phone: typing.Union[str, Validator] = PhoneNumberValidator(logger=False, debug=True)
    #     email: typing.Union[str, Validator] = EmailIDValidator(logger=True, debug=True, reassign=False)
    #     credit_card: typing.Union[str, Validator] = PaymentCardValidator(logger=False, debug=True)
    #     date: typing.Union[datetime.datetime, Validator] = DateValidator(logger=False, debug=True, default=datetime.datetime.utcnow)
    #     int_list: typing.Union[dict[str, list[set[int]]], Validator ]= DictionaryValidator(debug=True)
    #     choice_item: typing.Union[str, Validator] = Validator(in_choice=["a", "b", "c"])
    #     nt: typing.Union[typing.NamedTuple , Validator] = Validator(debug=True)


   
    # T = typing.TypeVar("T")
    # cls = typing.Generic[T]
    # print(issubclassx(cls, typing.Generic))
    # t = Test(email="z@a.com", int_list={"hello": [{2, 3}, {1, 2}]})
    # t.email = "x@y.com"
