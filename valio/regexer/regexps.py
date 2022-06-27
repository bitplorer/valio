# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT



from functools import reduce
from pprint import pformat
from typing import Union

__all__ = [
    "PatternType",
    "Pattern",
    "All",
    "Any",
    "SetOf",
    "Escape",
    "CapturingGroup",
    "NonCapturingGroup",
    "NamedCapturingGroup",
    "IfEarlierNamedCapturedGroup",
    "Comment",
    "StartsWith",
    "EndsWith",
    "StartOfString",
    "EndOfString",
    "WordBoundary",
    "IfPrecededBy",
    "IfNotPrecededBy",
    "IfFollowedBy",
    "IfNotFollowedBy",
    "IfGroupNameMatched",
]


class PatternType(object):
    def __init__(
            self,
            pattern: Union[str, bytes, "PatternType", "Pattern", None, object],
            alias: str = None,
    ):
        self.pattern = (
            pattern.pattern
            if hasattr(pattern, "pattern")
            else pattern
            if isinstance(pattern, (str, bytes))
            else None
        )
        self.raw_pattern = (
            pattern.raw_pattern if hasattr(pattern, "raw_pattern") else self.pattern
        )
        self.quantifier = pattern.quantifier if hasattr(pattern, "quantifier") else fr""
        self.alias = alias or pattern.alias if hasattr(pattern, "alias") else self.alias \
            if hasattr(self, "alias") and any(self.alias) else fr""

    def __and__(self, other):
        if not isinstance(other, PatternType):
            raise TypeError(
                f"expected {type(self).__name__} type, "
                f"got {type(other).__name__} instead"
            )
        if all(
                [
                    isinstance(self.pattern, PatternType),
                    isinstance(other.pattern, PatternType),
                ]
        ):
            return AND(self.pattern, other.pattern)
        return AND(self, other)

    def __or__(self, other):
        if not isinstance(other, PatternType):
            raise TypeError(
                f"expected {type(self).__name__} type, "
                f"got {type(other).__name__} instead"
            )
        if all(
                [
                    isinstance(self.pattern, PatternType),
                    isinstance(other.pattern, PatternType),
                ]
        ):
            return OR(self.pattern, other.pattern)
        return OR(self, other)

    def __neg__(self):
        return NOT(self)

    def __iter__(self):
        for _ in [self.pattern]:
            yield _

    def __str__(self):
        return self.pattern

    def __repr__(self):
        return pformat(fr"<{__name__}.PatternType({repr(self.pattern)}) object at {hex(hash(id(self)))}>")

    def __set_name__(self, owner, name):
        if self.alias is None or not any([self.alias]):
            self.alias = name


class OR(PatternType):
    def __init__(
            self,
            first_pattern: PatternType,
            second_pattern: PatternType,
    ):
        _pattern = Pattern(f"{first_pattern.pattern}|{second_pattern.pattern}") if not isinstance(first_pattern,
                                                                                                  OR) else Pattern(
            f"{first_pattern.raw_pattern}|{second_pattern.pattern}")
        self.pattern = NonCapturingGroup(_pattern).pattern
        self.raw_pattern = _pattern.raw_pattern
        self.allow_set = not any([first_pattern.quantifier, second_pattern.quantifier])
        self.alias = " or ".join([first_pattern.alias, second_pattern.alias])
        super(OR, self).__init__(self)


class AND(PatternType):
    def __init__(
            self,
            first_pattern: PatternType,
            second_pattern: PatternType,
    ):
        self.pattern = f"{first_pattern.pattern}{second_pattern.pattern}"
        self.allow_set = not any([first_pattern.quantifier, second_pattern.quantifier])
        self.alias = "".join([first_pattern.alias, second_pattern.alias])
        super(AND, self).__init__(self)


class NOT(PatternType):
    def __init__(self, pattern: Union[PatternType, "SetOf"]):
        self.pattern = (
            f"!{pattern.pattern}"
            if not isinstance(pattern, SetOf)
            else (~pattern).pattern
        )
        super(NOT, self).__init__(self)


class Value(object):
    def __init__(self, min_value: int = None, max_value: int = None):
        _min_value = min_value or 0
        _max_value = max_value or _min_value
        if _max_value < _min_value:
            raise ValueError(
                f"expect max_value to be equal to or greater than {_min_value}, got {_max_value} instead"
            )

        self._min = min_value
        self._max = max_value
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._min is not None:
            if value < self._min:
                raise ValueError(
                    f"expect value to be equal to or greater than {self._min}, got {value} instead"
                )
        if self._max is not None:
            if value > self._max:
                raise ValueError(
                    f"expect value to be equal to or less than {self._max}, got {value} instead"
                )
        self._value = value


class Quantifier(PatternType):
    def __init__(
            self,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
    ):
        if count_min is not None:
            if count_min < 0:
                raise ValueError(
                    f"expect count_min to be equal to or greater than 0, got {count_min} instead"
                )
        positive = Value(min_value=count_min or 0)
        _min = positive.value = count_min or 0
        _max = positive.value = count_max or _min
        del positive
        count = (
            fr""
            if all([count_min is None, count_max is None])
            else (
                f"{{{_min},{_max if count_max is not None else ''}}}"
                if count_min != count_max
                else f"{{{count_min}}}"
                if count_min is not None
                else f"{{{_min},{_max if count_max is not None else ''}}}"
            )
        )
        count_map = {f"{{0,}}": f"*", f"{{1,}}": f"+", f"{{0,1}}": f"?"}
        try:
            self.quantifier = (
                f"{count_map[count]}" if greedy else f"{count_map[count]}?"
            )
        except KeyError:
            self.quantifier = fr"{count}" if greedy else fr"{count}?"
        super(Quantifier, self).__init__(self)


class Pattern(PatternType):
    def __init__(
            self,
            /,  # NOQA
            pattern: Union[str, bytes],
            raw_pattern: Union[str, bytes, None] = None,
            quantifier: str = None,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            alias: str = None,
    ):
        if any([all([count, count_min]), all([count, count_max])]):
            raise ValueError(
                f"count and count_min or count and count_max "
                f"values can not be used together"
            )
        quantifier = (
                quantifier
                or Quantifier(
            count_min=count_min or count if count is not None else count_min,
            count_max=count_max or count if count is not None else count_max, greedy=greedy
        ).quantifier
        )
        self.raw_pattern = raw_pattern if raw_pattern is not None else pattern
        self.quantifier = quantifier
        self.pattern = fr"{pattern}{quantifier}"
        super(Pattern, self).__init__(self)
        if alias is not None:
            self.alias = alias


class All(PatternType):
    def __init__(self, *patterns: PatternType):
        self.pattern = (
            reduce(lambda x, y: x & y, iter(patterns)) if any(patterns) else ""
        )
        super(All, self).__init__(self.pattern)


class Any(PatternType):
    def __init__(self, *patterns: PatternType):
        self.pattern = (
            reduce(lambda x, y: (x | y), iter(patterns)) if any(patterns) else f"."
        )
        super(Any, self).__init__(self.pattern)


class SetOf(PatternType):
    def __init__(
            self,
            pattern: Union[PatternType, Pattern, "SetOf"],
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            alias: str = None
    ):
        if any([all([count, count_min]), all([count, count_max])]):
            raise ValueError(
                f"count and count_min or count and count_max "
                f"values can not be used together"
            )
        if isinstance(pattern, (OR, AND)):
            if not pattern.allow_set:
                raise SyntaxError(
                    "expected SetOf(A) * SetOf(B) syntax, got SetOf(A*B) syntax instead"
                )
        set_quantifier = Quantifier(
            count_min=count_min or count if count is not None else count_min,
            count_max=count_max or count if count is not None else count_max, greedy=greedy
        ).quantifier
        self.raw_pattern = pattern.raw_pattern
        if any(set_quantifier) and any(pattern.quantifier):
            raise ValueError(
                fr"pattern quantifiers {pattern.quantifier} already exist, "
                fr"{SetOf.__name__} quantifiers can't be set"
            )
        self.quantifier = (
            set_quantifier if not any(pattern.quantifier) else pattern.quantifier
        )
        negate = pattern.set_negated if hasattr(pattern, "set_negated") else False
        self.pattern = (
            f"[{self.raw_pattern}]{self.quantifier}"
            if negate is None or not negate
            else f"[^{self.raw_pattern}]{self.quantifier}"
        )
        self.set_negated = negate
        super(SetOf, self).__init__(self)

    def __invert__(self):
        self.set_negated = ~self.set_negated
        return SetOf(self)


class Escape(PatternType):
    def __new__(cls, *args, **kwargs):
        if not any(kwargs) and len(args) == 1 and isinstance(args[0], SetOf):
            return ~args[0]
        __class__ = super(Escape, cls).__new__(*args, **kwargs)
        return __class__

    def __init__(self, pattern: PatternType):
        self.pattern = f"\\{pattern.raw_pattern}"
        self.raw_pattern = pattern.raw_pattern
        super(Escape, self).__init__(self)

    def __or__(self, other):
        if isinstance(other, Escape):
            return Escape(Pattern(f"{self.raw_pattern}|{other.raw_pattern}"))
        else:
            super(Escape, self).__or__(other)

    def __and__(self, other):
        if isinstance(other, Escape):
            return Escape(Pattern(f"{self.raw_pattern}{other.raw_pattern}"))
        else:
            super(Escape, self).__or__(other)


class CapturingGroup(PatternType):
    def __init__(
            self,
            pattern: PatternType,
            count_min: int = None,
            count: int = None,
            count_max: int = None,
            greedy: bool = True,
    ):
        self.pattern = Pattern(
            pattern=fr"({pattern.pattern})",
            count_min=count_min,
            count=count,
            count_max=count_max,
            greedy=greedy,
        )
        self.alias = pattern.alias
        super(CapturingGroup, self).__init__(self.pattern)


class NonCapturingGroup(PatternType):
    def __init__(
            self,
            pattern: PatternType,
            count_min: int = None,
            count: int = None,
            count_max: int = None,
            greedy: bool = True,
    ):
        self.pattern = Pattern(
            pattern=fr"(?:{pattern.pattern if not isinstance(pattern, OR) else pattern.raw_pattern})",
            count_min=count_min,
            count=count,
            count_max=count_max,
            greedy=greedy,
        )
        self.raw_pattern = pattern.raw_pattern
        self.alias = pattern.alias
        super(NonCapturingGroup, self).__init__(self.pattern)


class NamedCapturingGroup(PatternType):
    def __init__(
            self,
            name: str,
            pattern: PatternType,
            count_min: int = None,
            count: int = None,
            count_max: int = None,
            greedy: bool = True,
    ):
        if any([all([count, count_min]), all([count, count_max])]):
            raise ValueError(
                f"count and count_min or count and count_max "
                f"values can not be used together"
            )

        self.quantifier = Quantifier(
            count_min=count_min or count if count is not None else count_min,
            count_max=count_max or count if count is not None else count_max, greedy=greedy
        ).quantifier
        self.raw_pattern = pattern.pattern
        self.pattern = fr"(?P<{name}>{self.raw_pattern}){self.quantifier}"
        self.name = name
        self.alias = pattern.alias
        super(NamedCapturingGroup, self).__init__(self)


class IfEarlierNamedCapturedGroup(PatternType):
    def __init__(self, group_name: NamedCapturingGroup):
        self.pattern = f"(?P={group_name.name})"
        self.alias = group_name.alias
        super(IfEarlierNamedCapturedGroup, self).__init__(self)


class Comment(PatternType):
    def __init__(self, comment_msg: str):
        self.pattern = f"(?#{comment_msg})"
        super(Comment, self).__init__(self)


class StartsWith(PatternType):
    def __init__(self, pattern: PatternType):
        self.pattern = f"^{pattern.pattern}"
        self.alias = pattern.alias
        super(StartsWith, self).__init__(self.pattern)


class EndsWith(PatternType):
    def __init__(self, pattern: PatternType):
        self.pattern = f"{pattern.pattern}$"
        self.alias = pattern.alias
        super(EndsWith, self).__init__(self.pattern)


class StartOfString(PatternType):
    def __init__(self, pattern: PatternType = None):
        self.pattern = fr"\A" if pattern is None else fr"\A{pattern.pattern}"
        self.alias = pattern.alias
        super(StartOfString, self).__init__(self.pattern)


class EndOfString(PatternType):
    def __init__(self, pattern: PatternType = None):
        self.pattern = fr"\Z" if pattern is None else fr"{pattern.pattern}\Z"
        self.alias = pattern.alias
        super(EndOfString, self).__init__(self.pattern)


class WordBoundary(PatternType):
    def __init__(self, pattern: PatternType):
        self.pattern = fr"\b{pattern.pattern}\b"
        self.alias = pattern.alias
        super(WordBoundary, self).__init__(self.pattern)


class IfPrecededBy(PatternType):
    def __init__(self, pattern: PatternType):
        self.pattern = f"(?<={pattern.pattern})"
        self.alias = pattern.alias
        super(IfPrecededBy, self).__init__(self)


class IfNotPrecededBy(PatternType):
    def __init__(self, pattern: PatternType):
        self.pattern = f"(?<!{pattern.pattern})"
        self.alias = pattern.alias
        super(IfNotPrecededBy, self).__init__(self)


class IfFollowedBy(PatternType):
    def __init__(self, pattern: PatternType):
        self.pattern = f"(?={pattern.pattern})"
        self.alias = pattern.alias
        super(IfFollowedBy, self).__init__(self)


class IfNotFollowedBy(PatternType):
    def __init__(self, pattern: PatternType):
        self.pattern = f"(?!{pattern.pattern})"
        self.alias = pattern.alias
        super(IfNotFollowedBy, self).__init__(self)


class IfGroupNameMatched(PatternType):
    def __init__(
            self,
            named_group: NamedCapturingGroup,
            pattern: PatternType,
            fallback_pattern: PatternType = None,
    ):
        self.pattern = (
            f"(?({named_group.name}){pattern.pattern}|{fallback_pattern.pattern})"
            if fallback_pattern is not None
            else f"(?({named_group.name}){pattern.pattern})"
        )
        self.alias = pattern.alias
        super(IfGroupNameMatched, self).__init__(self)


if __name__ == "__main__":
    from pyparsing import Regex

    hyphen = Pattern(r"-", alias="-")
    colon = Pattern(r":", alias=":")
    backslash = Pattern(r"/", alias="/")
    space = Pattern(r"\s", count_min=0, greedy=False, alias=" ")
    four_digits = space & Pattern(r"\d", count=4, alias="dddd") & space
    two_digits = space & Pattern(r"\d", count=2, alias="dd") & space

    # European Date Format
    eu_date_with_hyphen = four_digits & hyphen & two_digits & hyphen & two_digits
    eu_date_with_colon = four_digits & colon & two_digits & colon & two_digits
    eu_date_with_backslash = four_digits & backslash & two_digits & backslash & two_digits
    eu_date = WordBoundary(eu_date_with_colon | eu_date_with_hyphen | eu_date_with_backslash)

    # Indian Date format
    ind_date_with_hyphen = two_digits & hyphen & two_digits & hyphen & four_digits
    ind_date_with_colon = two_digits & colon & two_digits & colon & four_digits
    ind_date_with_backslash = two_digits & backslash & two_digits & backslash & four_digits
    ind_date = WordBoundary(ind_date_with_hyphen | ind_date_with_colon | ind_date_with_backslash)

    start_str = StartOfString(space & Pattern("date") & space & colon & space)
    date_ = (start_str & eu_date) | (start_str & ind_date)

    print(date_.alias)
    print(date_.pattern)
    print(Regex(date_.pattern).re_match("date  : 2021:01:20"))
    print(Regex(date_.pattern).re_match("date: 2021/01/20"))
    print(Regex(date_.pattern).re_match("date : 01-20-2011"))
