# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import pyparsing as pp
from valio.regexer.regexps import Pattern

_email_regex = (
    r"(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"
    r'"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|'
    r'\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")'
    r"@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)"
    r"+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|"
    r"[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|"
    r"[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|"
    r"\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
)

# def email_pattern(text):
#     non_digit = ~SetOf(Digit(count_min=1))
#     non_special_chars = ~special_chars_set
#     filtered_start = StartsWith(non_digit | non_special_chars)
#     filtered_end = EndsWith(non_digit | non_special_chars)
#     commercial_at = Pattern(r"@", count=1)
#     word = WordGroups(count_min=3, count_max=254)
#     dot = Pattern(r".", count=1)
#     optional_dot = Pattern(dot.pattern, count=1, greedy=False)
#     optional_plus = Pattern(r"+", count=1, greedy=False)
#     optional_underscore = Pattern(r"_", count=1, greedy=False)
#     optional_words = WordGroups(count_min=0, greedy=False)
#     optionals = optional_words | optional_plus | optional_dot | optional_underscore | optional_words
#     mail_p = filtered_start & optionals & word & optionals & commercial_at & word & dot & filtered_end
#     mails = pp.Regex(mail_p.pattern)
#     return mails.re_match(text)

email_pattern = Pattern(_email_regex, alias="person@example.com")


def get_email(text):
    mails = pp.Regex(email_pattern.pattern)
    return mails.re_match(text)
