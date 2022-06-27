# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT



import pytest
from valio.regexer import regexps, relib
from valio.regexer.relib import patterns


def assert_pattern_has(
        quantifier: str,
        if_greedy: bool,
        with_count_min: int = None,
        with_count_max: int = None,
):
    O_9 = fr"0-9"  # NOQA
    a_zA_Z = fr"a-zA-Z"  # NOQA
    w = fr"\w"  # NOQA
    d = fr"\d"  # NOQA
    s = fr"\s"  # NOQA
    W = fr"\W"  # NOQA
    D = fr"\D"  # NOQA
    S = fr"\S"  # NOQA
    p_0_9 = regexps.Pattern(
        O_9, count_min=with_count_min, count_max=with_count_max, greedy=if_greedy
    ).pattern
    p_a_zA_Z = patterns.Pattern(  # NOQA
        a_zA_Z, count_min=with_count_min, count_max=with_count_max, greedy=if_greedy
    ).pattern
    p_w = regexps.Pattern(
        w, count_min=with_count_min, count_max=with_count_max, greedy=if_greedy
    ).pattern
    p_d = regexps.Pattern(
        d, count_min=with_count_min, count_max=with_count_max, greedy=if_greedy
    ).pattern
    p_s = regexps.Pattern(
        s, count_min=with_count_min, count_max=with_count_max, greedy=if_greedy
    ).pattern
    p_W = regexps.Pattern(  # NOQA
        W, count_min=with_count_min, count_max=with_count_max, greedy=if_greedy
    ).pattern
    p_D = regexps.Pattern(  # NOQA
        D, count_min=with_count_min, count_max=with_count_max, greedy=if_greedy
    ).pattern
    p_S = regexps.Pattern(  # NOQA
        S, count_min=with_count_min, count_max=with_count_max, greedy=if_greedy
    ).pattern

    assert p_0_9 == f"{O_9}{quantifier}", f"{O_9}{quantifier} != {p_0_9} error"
    assert (
            p_a_zA_Z == f"{a_zA_Z}{quantifier}"
    ), f"{a_zA_Z}{quantifier} != {p_a_zA_Z} error"
    assert p_w == f"{w}{quantifier}", f"{w}{quantifier} != {p_w} error"
    assert p_d == f"{d}{quantifier}", f"{d}{quantifier} != {p_d} error"
    assert p_s == f"{s}{quantifier}", f"{s}{quantifier} != {p_s} error"
    assert p_W == f"{W}{quantifier}", f"{W}{quantifier} != {p_W} error"
    assert p_D == f"{D}{quantifier}", f"{D}{quantifier} != {p_D} error"
    assert p_S == f"{S}{quantifier}", f"{S}{quantifier} != {p_S} error"


def test_pattern_for_set():
    O_9 = fr"0-9"  # NOQA
    a_zA_Z = fr"a-zA-Z"  # NOQA
    w = fr"\w"  # NOQA
    d = fr"\d"  # NOQA
    s = fr"\s"  # NOQA
    W = fr"\W"  # NOQA
    D = fr"\D"  # NOQA
    S = fr"\S"  # NOQA
    assert regexps.Pattern(O_9).raw_pattern == O_9, f"{O_9} error"
    assert regexps.Pattern(a_zA_Z).raw_pattern == a_zA_Z, f"{a_zA_Z} error"
    assert regexps.Pattern(w).raw_pattern == w, f"{w} error"
    assert regexps.Pattern(d).raw_pattern == d, f"{d} error"
    assert regexps.Pattern(s).raw_pattern == s, f"{s} error"
    assert regexps.Pattern(W).raw_pattern == W, f"{W} error"
    assert regexps.Pattern(D).raw_pattern == D, f"{D} error"
    assert regexps.Pattern(S).raw_pattern == S, f"{S} error"


def test_set_of():
    O_9 = fr"0-9"  # NOQA
    a_zA_Z = fr"a-zA-Z"  # NOQA
    w = fr"\w"  # NOQA
    d = fr"\d"  # NOQA
    s = fr"\s"  # NOQA
    W = fr"\W"  # NOQA
    D = fr"\D"  # NOQA
    S = fr"\S"  # NOQA
    assert regexps.SetOf(regexps.Pattern(O_9)).pattern == f"[{O_9}]", f"[{O_9}] error"
    assert (
            regexps.SetOf(regexps.Pattern(a_zA_Z)).pattern == fr"[{a_zA_Z}]"
    ), f"[{a_zA_Z}] error"
    assert regexps.SetOf(regexps.Pattern(w)).pattern == fr"[{w}]", f"{w} error"
    assert regexps.SetOf(regexps.Pattern(d)).pattern == fr"[{d}]", f"{d} error"
    assert regexps.SetOf(regexps.Pattern(s)).pattern == fr"[{s}]", f"{s} error"
    assert regexps.SetOf(regexps.Pattern(W)).pattern == fr"[{W}]", f"{W} error"
    assert regexps.SetOf(regexps.Pattern(D)).pattern == fr"[{D}]", f"{D} error"
    assert regexps.SetOf(regexps.Pattern(S)).pattern == fr"[{S}]", f"{S} error"


def test_pattern():
    assert_pattern_has(quantifier=fr"?", if_greedy=False)
    assert_pattern_has(quantifier=fr"", if_greedy=True)
    assert_pattern_has(quantifier=fr"*?", with_count_min=0, if_greedy=False)
    assert_pattern_has(quantifier=fr"*", with_count_min=0, if_greedy=True)
    assert_pattern_has(quantifier=fr"+?", with_count_min=1, if_greedy=False)
    assert_pattern_has(quantifier=fr"+", with_count_min=1, if_greedy=True)
    assert_pattern_has(quantifier=fr"??", with_count_max=1, if_greedy=False)
    assert_pattern_has(quantifier=fr"?", with_count_max=1, if_greedy=True)
    assert_pattern_has(
        quantifier=fr"??", with_count_min=0, with_count_max=1, if_greedy=False
    )
    assert_pattern_has(
        quantifier=fr"?", with_count_min=0, with_count_max=1, if_greedy=True
    )
    assert_pattern_has(
        quantifier=fr"{{{0},{9}}}", with_count_min=0, with_count_max=9, if_greedy=True
    )
    assert_pattern_has(
        quantifier=f"{{{1}}}?", with_count_min=1, with_count_max=1, if_greedy=False
    )
    assert_pattern_has(
        quantifier=f"{{{1}}}", with_count_min=1, with_count_max=1, if_greedy=True
    )


def test_preceded_by():
    pattern_a = regexps.IfPrecededBy(
        regexps.All(
            regexps.EndsWith(
                regexps.SetOf((patterns.WordGroups() | patterns.DigitGroups()))
            ),
            patterns.WhiteSpace(count_max=2),
            regexps.SetOf(regexps.Pattern(fr"\w", count_min=1))
            & regexps.SetOf(regexps.Pattern(fr"\d")),
        )
    ).pattern

    preceding_special_chars = patterns.IfPreceding(
        relib.special_chars_set, name="special_chars_set"
    )

    pattern_b = regexps.IfGroupNameMatched(
        preceding_special_chars.named_capturing_group,
        regexps.SetOf(regexps.Pattern(fr"\w", count_max=1, greedy=False)),
        patterns.a_zA_Z,
    ).pattern

    pattern_c = regexps.SetOf(patterns.Word(count_min=2)) & regexps.SetOf(
        patterns.Digit(count_min=2)
    ) | ~regexps.SetOf(patterns.Word(count_min=1)) & regexps.NonCapturingGroup(
        # name="Year",
        pattern=regexps.WordBoundary(
            regexps.StartsWith(
                regexps.SetOf(patterns.Digit(count_min=2, count_max=4, greedy=False))
            )
            & regexps.Pattern(pattern=fr":", count_min=1, count_max=1)
            & regexps.EndsWith(~regexps.SetOf(patterns.Word(count_min=4)))
        ),
    )
    assert (
            pattern_a == fr"(?<=[\w|\d]$\s{{{0},{2}}}[\w]+[\d])"
    ), fr"{pattern_a} != (?<=[\w|\d]$\s{{{0},{2}}}[\w]+[\d])"
    assert (
            preceding_special_chars.named_capturing_group.pattern
            == r"(?P<special_chars_set>(?<=[!#$%&'*+/=?^_`{|}~-]))"
    ), fr"{preceding_special_chars.named_capturing_group} != (?P<special_chars_set>(?<=[!#$%&'*+/=?^_`{{|}}~-]))"
    assert (
            pattern_b == r"(?(special_chars_set)[\w]??|[a-zA-Z])"
    ), fr"{pattern_b} != (?(special_chars_set)[\w]??|[a-zA-Z])"


def main_test():
    test_pattern()
    test_set_of()
    test_pattern_for_set()
    # test_preceded_by()


if __name__ == "__main__":
    pytest.main(main_test())
