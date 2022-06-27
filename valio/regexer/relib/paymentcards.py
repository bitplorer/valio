# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from pyparsing import Regex
from valio.regexer.regexps import (CapturingGroup, EndsWith, IfNotFollowedBy,
                                   NamedCapturingGroup, NonCapturingGroup,
                                   Pattern, SetOf, StartsWith, WordBoundary)

__all__ = [
    "is_card_of_visa",
    "is_card_of_amex",
    "is_card_of_mastercard",
    "is_card_of_discover",
    "is_card_of_rupay",
    "is_valid_payment_card",
    "PaymentCard",
    "valid_from",
    "valid_thr"
]

# refer : https://github.com/raymondjavaxx/creditcardjs/blob/master/js/creditcard.js
# visa = r"^4[0-9]{12}([0-9]{3})?$"
# the visa pattern is replicated with Pattern
O_9 = Pattern(r"0-9")
visa = StartsWith(Pattern(r"4")) \
       & SetOf(O_9, count=12) \
       & EndsWith(CapturingGroup(SetOf(O_9, count=3), greedy=False))
visa = WordBoundary(visa)

# mastercard = r"^5[1-5][0-9]{14}$"
# the mastercard pattern is replicated with Pattern
mastercard = StartsWith(Pattern(r"5")) \
             & SetOf(Pattern(r"1-5")) \
             & EndsWith(SetOf(O_9, count=14))
mastercard = WordBoundary(mastercard)

# amex = "^3[4|7][0-9]{13}$"
# the american express card pattern is replicated here with Pattern class
amex = StartsWith(Pattern(r"3")) \
       & SetOf(Pattern(r"4") | Pattern(r"7")) \
       & EndsWith(SetOf(O_9, count=13))
amex = WordBoundary(amex)

# discover = "^(?:6011|644[0-9]|65[0-9]{2})[0-9]{12}$"
# the discover card pattern is replicated using Pattern class
discover = StartsWith(
    NonCapturingGroup(Pattern(r"6011")
                      | Pattern(r"644") & SetOf(O_9)
                      | Pattern("65") & SetOf(O_9, count=2))
) \
           & EndsWith(SetOf(O_9, count=12))

# refer: https://stackoverflow.com/questions/60785582/how-to-make-regular-expression-to-detect-rupay-debit-card
# Rupay Card = ^6(?!(?:011|44[0-9]|5[0-9]{2}))(?:0[0-9]{14}|52[12][0-9]{12})$
# the rupay card patter
rupay = StartsWith(Pattern("6")) \
        & IfNotFollowedBy(Pattern("011")
                          | (Pattern("44") & SetOf(O_9))
                          | (Pattern("5") & SetOf(O_9, count=2))
                          ) & EndsWith(NonCapturingGroup(Pattern("0")
                                                         & SetOf(O_9, count=14)
                                                         | Pattern("52") & SetOf(Pattern("12")) & SetOf(O_9, count=12)
                                                         )
                                       )


def luhn_correctness(card_number: str):
    ref: list = list()
    ref.extend(card_number)
    ref.reverse()
    _sum = 0
    odd = True
    for i, digit in enumerate(ref):
        digit = int(digit)
        if odd := not odd:
            digit *= 2
            if digit > 9:
                digit -= 9
        _sum += digit
    return _sum % 10 == 0


def is_card_of_visa(card_number: str):
    return luhn_correctness(card_number) \
           and Regex(visa.pattern).re_match(card_number)


def is_card_of_mastercard(card_number: str):
    return luhn_correctness(card_number) \
           and Regex(mastercard.pattern).re_match(card_number)


def is_card_of_amex(card_number: str):
    return luhn_correctness(card_number) \
           and Regex(amex.pattern).re_match(card_number)


def is_card_of_discover(card_number: str):
    return luhn_correctness(card_number) \
           and Regex(discover.pattern).re_match(card_number)


def is_card_of_rupay(card_number: str):
    return luhn_correctness(card_number) \
           and Regex(rupay.pattern).re_match(card_number)


def is_valid_payment_card(card_number: str):
    return luhn_correctness(card_number) \
           and Regex((visa | mastercard | amex | discover | rupay).pattern).scanString(card_number)


backslash = Pattern(r"\/", alias="/")
space = Pattern(r"\s", count_min=0, greedy=False, alias=" ")
m1 = SetOf(Pattern(r"0-1"), count=1)  # month unit place
m2 = SetOf(Pattern(r"0-2"), count=1)  # month secondary place
months = WordBoundary(space & Pattern((m1 & m2).pattern, alias="mm") & space)
years = WordBoundary(space & Pattern(r"\d", count=2, alias="yyyy") & space)
valid_from = NamedCapturingGroup(name="valid_from", pattern=(months & backslash & years))
valid_thr = NamedCapturingGroup(name="valid_through", pattern=(months & backslash & years))

del backslash, space, m1, m2, months, years, O_9, WordBoundary, SetOf, Pattern, StartsWith, EndsWith


class PaymentCard(object):

    def __init__(self, card_number, valid_through):
        self.is_valid_card = is_valid_payment_card(card_number)
        self.validity = Regex(valid_thr.pattern).scanString(valid_through)
        # card type
        card_type = None
        if is_card_of_visa(card_number):
            card_type = "visa"
        elif is_card_of_mastercard(card_number):
            card_type = "mastercard"
        elif is_card_of_amex(card_number):
            card_type = "amex"
        elif is_card_of_discover(card_number):
            card_type = "discover"
        elif is_card_of_rupay(card_number):
            card_type = "rupay"
        # card
        self.card_type = card_type

    def __bool__(self):
        return self.card_type is not None and any(self.validity)

    def __str__(self):
        return f"{self.__class__.__name__}" \
               f"(card_type={self.card_type if self.card_type is not None else 'invalid'})"
