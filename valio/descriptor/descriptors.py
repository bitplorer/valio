# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT



import typing
from dataclasses import astuple, dataclass, fields
from pprint import pformat
from typing import Any

from typingx import issubclassx
from valio.error import errors
from valio.logger import loggers

__all__ = ["Property", "NAME", "DEFAULT", "DOC", "DEBUG"]

T = typing.TypeVar('T')
PropBound = typing.TypeVar('PropBound', bound=typing.Union['Property', None])

Union = typing.Union[T, PropBound]

NAME = Union[str, PropBound]
DEFAULT = Union[Any, PropBound]
DOC = Union[str, PropBound]
DEBUG = Union[bool, PropBound]


@dataclass
class Property(loggers.Logger):
    """Property Class: its a base class for all property related usages.
    it has an inbuilt support for logging for each and every activity that
    the class does.

    Usage:

    >>> from dataclasses import dataclass
    ...
    >>> Name: str = Property()
    >>> Salary: int = Property()
    ...
    ...
    >>> @dataclass
    ... class Persons(object):
    ...     name: str = Name
    ...     salary: int = Salary
    ...
    >>> p = Persons()
    >>> p.name = "some name"
    >>> p.salary = "1000000"
    ...
    """

    name: NAME = None
    default: DEFAULT = None
    doc: DOC = None
    debug: DEBUG = None
    errors: Union[list, None] = None

    def __init__(
            self,
            name: NAME = None,
            default: DEFAULT = None,
            doc: DOC = None,
            debug: DEBUG = None,
            **kwargs,
    ):
        if name is None or isinstance(name, str):
            self.name = name
        else:
            raise TypeError(
                f"name expected type {str.__name__} value, "
                f"got {type(name).__name__} type instead"
            )

        if doc is None or isinstance(doc, str):
            self.doc = doc
        else:
            raise TypeError(
                f"doc expected type {str.__name__} value, "
                f"got {type(doc).__name__} type instead"
            )

        if debug is None or isinstance(debug, bool):
            self.debug = debug  # or environments.DEBUG
        else:
            raise TypeError(
                f"debug expected type {bool.__name__} value, "
                f"got {type(debug).__name__} type instead"
            )
        self.default = default
        self.annotation = getattr(self, "annotation", None)
        self._dict = None

        super(Property, self).__init__(**kwargs)

    def pre_set(self, obj, value):
        """All the pre-processing before setting any value is done via
        this api.
        """
        return value

    def post_set(self, obj, value):
        """All the post-processing after setting any value is done via
        this api.
        """
        return value

    def pre_get(self, obj, value):
        """All the pre-processing before getting any value is done via
        this api.
        """
        return value

    def post_get(self, obj, value):
        """All the pre-processing after getting any value is done via
        this api.
        """
        return value

    def pre_delete(self, obj, value):
        """All the pre-processing before deleting any value is done via
        this api.
        """
        return value

    def post_delete(self, obj, value):
        """All the pre-processing after deleting any value is done via
        this api.
        """
        return value

    def _set_name(self, owner, name, logger):
        if self.errors is None:
            self.errors = []

        # set name
        try:
            if self.name is None:
                self.name = name
                if logger:
                    logger.info(f"assigned: {owner.__name__}.{name}")

            # # if name is set ensure names match.
            elif name != self.name and self.annotation == owner.__annotations__.get(name, None):
                raise AttributeError(
                    f"{self.name} != {name}, attribute names did not match"
                )

        except (RuntimeError, errors.SetPropertyError, Exception) as name_err:
            if logger:
                logger.error(name_err)
            self.errors.append(name_err)
            raise name_err

    def _may_set_or_ensure_annotation_match(self, owner, name, logger):
        if self.errors is None:
            self.errors = []

        # set annotations
        try:
            # if owner has __annotations__ set, ensure annotations match
            # else assign annotations if any available

            if "__annotations__" not in owner.__dict__:
                owner.__annotations__ = dict()
            if name in owner.__annotations__:
                if self.annotation is None:
                    self.annotation = owner.__annotations__[name]
                else:
                    self_annotation = self.annotation
                    owner_annotation = owner.__annotations__[name]
                    if not issubclassx(owner_annotation, self_annotation):
                        owner_annotation_name = (
                            owner_annotation.__name__
                            if hasattr(owner_annotation, "__name__")
                            else str(owner_annotation)
                        )
                        self_annotation_name = (
                            self_annotation.__name__
                            if hasattr(self_annotation, "__name__")
                            else str(self_annotation)
                        )
                        raise TypeError(
                            f"{owner.__name__}.{self.name}: {owner_annotation_name}"
                            f" annotation did not match {type(self).__qualname__}: "
                            f"{self_annotation_name}"
                        )
                    if owner_annotation != self.annotation:
                        self.annotation = owner_annotation
            else:
                if self.annotation:
                    owner.__annotations__[name] = self.annotation
            # https://github.com/python/cpython/blob/1b293b60067f6f4a95984d064ce0f6b6d34c1216/Lib/typing.py#L1787-L1811
            # self.__supertype__ = owner.__annotations__[name]
            # self.__name__ = name
        except (RuntimeError, errors.SetPropertyError, Exception) as annotation_err:
            if logger:
                logger.error(annotation_err)
            self.errors.append(annotation_err)
            raise annotation_err

    def _set_docs(self, owner, name, logger):
        owner_annotation = owner.__annotations__[name]
        if self.errors is None:
            self.errors = []

        # set or extend docs for the class
        try:
            owner.__doc__ = owner.__doc__ or f"Class: {owner.__name__}"

            owner.__doc__ += (
                (
                    f"\n\t:param {owner_annotation} {str(self)}: {self.doc}"
                    if self.annotation
                    else f"\n\t:param {str(self)}: {self.doc}"
                )
                if self.doc is not None
                else (
                    f"\n\t:param {owner_annotation} {str(self)}:"
                    if self.annotation
                    else f"\n\t:param {str(self)}:"
                )
            )
        except (Exception,) as doc_err:
            if logger:
                logger.error(doc_err)
            self.errors.append(doc_err)
            raise doc_err

    def __set_name__(self, owner, name):
        logger = (
            self.get_logger(owner.__name__, name)
            if name is not None and self.logger is not False
            else None
        )
        if logger:
            _name = (
                f"{type(self).__name__}({self.name})"
                if self.name is not None
                else f"{type(self).__name__}"
            )
            logger.info(f"{_name}: assigning as property : {owner.__name__}.{name}")

        if self.errors is None:
            self.errors = []

        self._set_name(owner=owner, name=name, logger=logger)
        self._may_set_or_ensure_annotation_match(owner=owner, name=name, logger=logger)
        self._set_docs(owner=owner, name=name, logger=logger)

    def __set__(self, obj, value):
        """sets descriptor field"""
        class_name = type(obj).__name__
        attr_name = self.name

        if logger := self.logger:
            logger.info(f"setting: {class_name}.{attr_name}")
        
        try:
            value = value or (self.default \
                if not callable(self.default) else self.default()) \
                if self.default is not None else value
            value = self.pre_set(obj, value)
            obj.__dict__[self.name] = value
            if logger:
                logger.info(f"set: {class_name}.{attr_name}")
            self.post_set(obj, value)
        except (errors.SetPropertyError, Exception) as spe:
            if logger:
                logger.error(spe)
            self.errors.append(spe)
            if self.debug:
                raise spe

    def __get__(self, obj, obj_type=None):
        """gets descriptor field"""
        if obj is None:
            return #self
        
        class_name = type(obj).__name__
        attr_name = self.name
        if logger := self.logger:
            logger.info(f"getting: {class_name}.{attr_name}")
        error = False
        try:
            self.pre_get(obj, self.name)
            return obj.__dict__[self.name]
        except (errors.GetPropertyError, Exception) as gpe:
            if logger:
                logger.error(gpe)
            error = True
            self.errors.append(gpe)
            if self.debug:
                raise gpe
        finally:
            if logger and not error:
                logger.info(f"got: {class_name}.{attr_name}")
            try:
                self.post_get(obj, self.name)
            except (Exception,) as post_get_err:
                if logger:
                    logger.error(post_get_err)
                self.errors.append(post_get_err)
                if self.debug:
                    raise post_get_err

    def __delete__(self, obj):
        """deletes descriptor"""
        class_name = type(obj).__name__
        attr_name = self.name
        if logger := self.logger:
            logger.info(f"deleting: {class_name}.{attr_name}")
        error = False
        try:
            self.pre_delete(obj, self.name)
            del obj.__dict__[self.name]
            self.post_delete(obj, self.name)

        except (errors.DeletePropertyError, Exception) as dpe:
            if logger:
                logger.error(dpe)
            error = True
            self.errors.append(dpe)
            if self.debug:
                raise dpe
        finally:
            if logger and not error:
                logger.info(f"deleted: {class_name}.{attr_name}")

    def __str__(self):
        return str(self.name)

    def dict(self):
        if self._dict is None:
            self._dict = dict(zip(map(
                lambda field: field.name, fields(self)),
                astuple(self)), **self.kwargs)
        return self._dict

    def __repr__(self):
        return pformat(self._dict)

# if __name__ == "__main__":
#     from dataclasses import dataclass
#
#     name_field = Property(annotation=str)
#     salary_field = Property(annotation=int, log_levels=["INFO", "DEBUG"])
#
#     @dataclass
#     class Person(object):
#         name: str = name_field
#         salary: int = salary_field
#
#     t = Person()
#     t.name = "some shitty name"
#     t.salary = 2222
#     print(t.name)
#     print(t.__doc__)
#     print(Property(name="2", doc="helping") == Property("2"))
#     import pprint
# pprint.pprint(salary_field.as_dict())
