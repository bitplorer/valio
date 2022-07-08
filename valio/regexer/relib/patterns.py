# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from valio.regexer.regexps import *

__all__ = [
    "WhiteSpace",
    "NonWhiteSpace",
    "Word",
    "NonWord",
    "Digit",
    "NonDigit",
    "WordGroups",
    "NonWordGroups",
    "DigitGroups",
    "NonDigitGroups",
    "IfPreceding",
    "IfNotPreceding",
]


class WhiteSpace(PatternType):
    def __init__(
            self,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            alias: str = None,
    ):
        self.pattern = Pattern(
            fr"\s",
            count=count,
            count_min=count_min,
            count_max=count_max,
            greedy=greedy,
            alias=alias,
        )
        super(WhiteSpace, self).__init__(self.pattern)


class NonWhiteSpace(PatternType):
    def __init__(
            self,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            alias: str = None,
    ):
        self.pattern = Pattern(
            fr"\S",
            count=count,
            count_min=count_min,
            count_max=count_max,
            greedy=greedy,
            alias=alias,
        )
        super(NonWhiteSpace, self).__init__(self.pattern)


class Word(PatternType):
    def __init__(
            self,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            alias: str = None,
    ):
        self.pattern = Pattern(
            pattern=fr"\w",
            count=count,
            count_min=count_min,
            count_max=count_max,
            greedy=greedy,
            alias=alias,
        )
        super(Word, self).__init__(self.pattern)


class NonWord(PatternType):
    def __init__(
            self,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            alias: str = None,
    ):
        self.pattern = Pattern(
            pattern=fr"\W",
            count=count,
            count_min=count_min,
            count_max=count_max,
            greedy=greedy,
            alias=alias,
        )
        super(NonWord, self).__init__(self.pattern)


class Digit(PatternType):
    def __init__(
            self,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            alias: str = None,
    ):
        self.pattern = Pattern(
            pattern=fr"\d",
            count=count,
            count_min=count_min,
            count_max=count_max,
            greedy=greedy,
            alias=alias,
        )
        super(Digit, self).__init__(self.pattern)


class NonDigit(PatternType):
    def __init__(
            self,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            alias: str = None,
    ):
        self.pattern = Pattern(
            pattern=fr"\D",
            count=count,
            count_min=count_min,
            count_max=count_max,
            greedy=greedy,
            alias=alias,
        )
        super(NonDigit, self).__init__(self.pattern)


class WordGroups(PatternType):
    def __init__(
            self,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            name: str = "words",
            alias: str = None,
    ):
        self.pattern = Word(
            count=count,
            count_min=count_min,
            count_max=count_max,
            greedy=greedy,
            alias=alias,
        )
        self.named_capturing_group = NamedCapturingGroup(
            name=name, pattern=self.pattern
        )
        self.capturing_group = CapturingGroup(pattern=self.pattern)
        self.non_capturing_group = NonCapturingGroup(pattern=self.pattern)
        super(WordGroups, self).__init__(self.pattern)


class NonWordGroups(PatternType):
    def __init__(
            self,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            name: str = "non_words",
            alias: str = None,
    ):
        self.pattern = NonWord(
            count=count,
            count_min=count_min,
            count_max=count_max,
            greedy=greedy,
            alias=alias,
        )
        self.named_capturing_group = NamedCapturingGroup(
            name=name, pattern=self.pattern
        )
        self.capturing_group = CapturingGroup(pattern=self.pattern)
        self.non_capturing_group = NonCapturingGroup(pattern=self.pattern)
        super(NonWordGroups, self).__init__(self.pattern)


class DigitGroups(PatternType):
    def __init__(
            self,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            name: str = "digits",
            alias: str = None,
    ):
        self.pattern = Digit(
            count=count,
            count_min=count_min,
            count_max=count_max,
            greedy=greedy,
            alias=alias,
        )
        self.named_capturing_group = NamedCapturingGroup(
            name=name, pattern=self.pattern
        )
        self.capturing_group = CapturingGroup(pattern=self.pattern)
        self.non_capturing_group = NonCapturingGroup(pattern=self.pattern)
        super(DigitGroups, self).__init__(self.pattern)


class NonDigitGroups(PatternType):
    def __init__(
            self,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            name: str = "non_digits",
            alias: str = None,
    ):
        self.pattern = NonDigit(
            count=count,
            count_min=count_min,
            count_max=count_max,
            greedy=greedy,
            alias=alias,
        )
        self.named_capturing_group = NamedCapturingGroup(
            name=name, pattern=self.pattern
        )
        self.capturing_group = CapturingGroup(pattern=self.pattern)
        self.non_capturing_group = NonCapturingGroup(pattern=self.pattern)
        super(NonDigitGroups, self).__init__(self.pattern)


class IfPreceding(PatternType):
    def __init__(
            self,
            pattern: PatternType,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            name: str = "preceded_pattern",
            alias: str = None,
    ):
        self.pattern = Pattern(
            pattern=IfPrecededBy(pattern=pattern).pattern,
            count=count,
            count_min=count_min,
            count_max=count_max,
            greedy=greedy,
            alias=alias,
        )
        self.raw_pattern = pattern.raw_pattern
        self.capturing_group = CapturingGroup(pattern=self.pattern)
        self.non_capturing_group = NonCapturingGroup(pattern=self.pattern)
        self.named_capturing_group = NamedCapturingGroup(
            pattern=self.pattern, name=name
        )
        super(IfPreceding, self).__init__(self.pattern)


class IfNotPreceding(PatternType):
    def __init__(
            self,
            pattern: PatternType,
            count: int = None,
            count_min: int = None,
            count_max: int = None,
            greedy: bool = True,
            name: str = "non_preceded_pattern",
            alias: str = None,
    ):
        self.pattern = Pattern(
            pattern=IfNotPrecededBy(pattern=pattern).pattern,
            count=count,
            count_min=count_min,
            count_max=count_max,
            greedy=greedy,
            alias=alias,
        )
        self.capturing_group = CapturingGroup(pattern=pattern)
        self.non_capturing_group = NonCapturingGroup(pattern=self.pattern)
        self.named_capturing_group = NamedCapturingGroup(
            pattern=self.pattern, name=name
        )
        super(IfNotPreceding, self).__init__(self.pattern)


a_z = SetOf(Pattern(r"a-z"))
A_Z = SetOf(Pattern(r"A-Z"))
a_zA_Z = a_z & A_Z
