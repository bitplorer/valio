# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT



from valio.regexer.regexps import Pattern, SetOf

# Specials (32-47)


space = Pattern(pattern=r"\s")
exclamation_point = Pattern(pattern=r"!")
quotation_mark = Pattern(pattern='"')
pound_sign = Pattern(pattern=r"#")
dollar_sign = Pattern(pattern=r"$")
percent_sign = Pattern(pattern=r"%")
ampersand = Pattern(pattern=r"&")
apostrophe = Pattern(pattern=r"'")
left_parenthesis = Pattern(pattern=fr"(")
right_parenthesis = Pattern(pattern=fr")")
asterisk = Pattern(pattern=r"*")
plus_sign = Pattern(pattern=r"+")
comma = cedilla = Pattern(pattern=r",")
hyphen = minus_sign = Pattern(pattern=r"-")
period = decimal_point = Pattern(pattern=r".")
slant = solidus = Pattern(pattern=r"/")

special_chars = (
        exclamation_point
        & quotation_mark
        & pound_sign
        & dollar_sign
        & percent_sign
        & ampersand
        & apostrophe
        & left_parenthesis
        & right_parenthesis
        & asterisk
        & plus_sign
        & comma
        & hyphen
        & period
        & slant
)

special_chars_set = SetOf(special_chars)
