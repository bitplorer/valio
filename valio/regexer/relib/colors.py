# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


from valio.regexer.regexps import (CapturingGroup, NonCapturingGroup, Pattern,
                                   SetOf, WordBoundary)
from valio.regexer.relib.special_chars import pound_sign

__all__ = [
    "r_hex_short",
    "r_hex_long",
    "r_rgb",
    "r_rgba",
    "r_hsl",
    "r_hsla"
]

space = Pattern(r"\s", count_min=0)
zx = Pattern(r"0x")
_hex_start = NonCapturingGroup((pound_sign | zx), greedy=False)
O_9 = Pattern(r"0-9")
a_f = Pattern(r"a-f")
O_9a_f_single_set = SetOf(O_9 & a_f)
O_9a_f_double_set = SetOf(O_9 & a_f, count=2)
_rgb_ss = CapturingGroup(O_9a_f_single_set)
_rgb_ss_opn = CapturingGroup(O_9a_f_single_set, greedy=False)
_rgb_ds = CapturingGroup(O_9a_f_double_set)
_rgb_ds_opn = CapturingGroup(O_9a_f_double_set, greedy=False)

####################################################################################
r_hex_short = space & _hex_start & _rgb_ss & _rgb_ss & _rgb_ss & _rgb_ss_opn & space
r_hex_long = space & _hex_start & _rgb_ds & _rgb_ds & _rgb_ds & _rgb_ds_opn & space
####################################################################################


O_1 = SetOf(Pattern(r"0-1"), count=1, greedy=False)
_2 = SetOf(Pattern(r"2"), count=1, greedy=False)
O_99 = SetOf(Pattern(r"0-9"), count=2, greedy=False)
O_55 = SetOf(Pattern(r"0-5"), count=2, greedy=False)
decimal_optional = NonCapturingGroup(Pattern(r"\.") & Pattern(r"\d", count_min=1), greedy=False)
O_255 = WordBoundary(((O_1 & O_99) & decimal_optional) | ((_2 & O_55) & decimal_optional))
_r_255 = fr'(\d{1,3}{decimal_optional})'
_r_comma = space & Pattern(r",") & space

#####################################################################################
r_rgb = fr'{space}rgb\({space}{_r_255}{_r_comma}{_r_255}{_r_comma}{_r_255}\){space}'
#####################################################################################

_r_alpha = fr'(\d{decimal_optional}|\.\d+|\d{1,2}%)'

###################################################################################################################
r_rgba = fr'{space}rgba\({space}{_r_255}{_r_comma}{_r_255}{_r_comma}{_r_255}{_r_comma}{_r_alpha}{space}\){space}'
###################################################################################################################

_r_h = fr'(-?\d+{decimal_optional}|-?\.\d+)(deg|rad|turn)?'
_r_sl = fr'(\d{1,3}{decimal_optional})%'

############################################################################################################
r_hsl = fr'{space}hsl\({space}{_r_h}{_r_comma}{_r_sl}{_r_comma}{_r_sl}{space}\){space}'
r_hsla = fr'{space}hsl\({space}{_r_h}{_r_comma}{_r_sl}{_r_comma}{_r_sl}{_r_comma}{_r_alpha}{space}\){space}'
############################################################################################################

# colors where the two hex characters are the same, if all colors match this the short version of hex colors can be used
repeat_colors = {int(c * 2, 16) for c in '0123456789abcdef'}
