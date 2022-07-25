# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from datetime import datetime
from re import IGNORECASE

import pyparsing as pp
from valio.regexer.regexps import (NamedCapturingGroup, NonCapturingGroup,
                                   Pattern, SetOf, WordBoundary)

__all__ = [
    "months",
    "years",
    "jan",
    "feb",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
    "day_numbers",
    "months_names",
    "months_numbers",
    "dates",
    "times",
    "eu_date",
    "ind_date",
    "get_date"
]

#####################################################################################
#               another better implementation with leap year filtering              #
#                          https://stackoverflow.com/a/10309472                     #
#                   with valid days and months formats.                             #
#               https://www.regular-expressions.info/branchreset.html               #
#####################################################################################

#####################################################################################
space = Pattern(r"\s", count_min=0, greedy=False, alias=" ")
optional_zero = Pattern(r"0", count_max=1, greedy=False)
_monthsToNum = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12
}
###################################################################################

# days
first_nine_days = optional_zero & SetOf(Pattern(r"1-9"), count=1)
tens_and_twenties = SetOf(Pattern(r"1-2"), count=1) & SetOf(Pattern(r"0-9"), count=1)
thirties = Pattern("3") & SetOf(Pattern(r"01"), count=1)
day_numbers = WordBoundary(
    space
    & Pattern(NonCapturingGroup(first_nine_days | tens_and_twenties | thirties).pattern, alias="DD")
    & space
)
rd = WordBoundary(space & NonCapturingGroup(Pattern(r"rd", alias="rd"), count_max=1, greedy=False) & space)
th = WordBoundary(space & NonCapturingGroup(Pattern(r"th", alias="th"), count_max=1, greedy=False) & space)
st = WordBoundary(space & NonCapturingGroup(Pattern(r"st", alias="st"), count_max=1, greedy=False) & space)
nd = WordBoundary(space & NonCapturingGroup(Pattern(r"nd", alias="nd"), count_max=1, greedy=False) & space)
day_postfix = rd | th | st | nd

# months
first_nine_months = optional_zero & SetOf(Pattern(r"1-9"), count=1)
tenth_to_twelth_months = Pattern(r"1", count=1) & SetOf(Pattern(r"0-2"), count=1)
months_numbers = Pattern((first_nine_months | tenth_to_twelth_months).pattern, alias="MM")

# january month
jan = WordBoundary(
    (Pattern(r"J", count=1) | Pattern(r"j", count=1))
    & Pattern(r"an")
    & NonCapturingGroup(Pattern(r"uary"), count_max=1, greedy=False)
)

# february month
feb = WordBoundary(
    (Pattern(r"F", count=1) | Pattern(r"f", count=1))
    & Pattern(r"eb")
    & NonCapturingGroup(Pattern(r"ruary"), count_max=1, greedy=False)
)

# march month
march = WordBoundary(
    (Pattern(r"M", count=1) | Pattern(r"m", count=1)) & Pattern(r"ar")
    & NonCapturingGroup(Pattern(r"ch"), count_max=1, greedy=False)
)

# april month
april = WordBoundary(
    (Pattern(r"A") | Pattern(r"a")) & NonCapturingGroup(Pattern(r"pr"), count=1)
    & NonCapturingGroup(Pattern(r"il"), count_max=1, greedy=False)
)

# may month
may = WordBoundary(
    (Pattern(r"M") | Pattern(r"m")) & NonCapturingGroup(Pattern(r"ay"), count=1)
)

# june month
june = WordBoundary(
    (Pattern(r"J") | Pattern(r"j"))
    & NonCapturingGroup(Pattern(r"un"), count=1)
    & NonCapturingGroup(Pattern(r"e"), count_max=1, greedy=False)
)

# july month
july = WordBoundary(
    (Pattern(r"J") | Pattern(r"j"))
    & NonCapturingGroup(Pattern(r"ul"))
    & NonCapturingGroup(Pattern(r"y"), count_max=1, greedy=False)
)

# august month
august = WordBoundary(
    (Pattern(r"A") | Pattern(r"a"))
    & NonCapturingGroup(Pattern(r"ug"))
    & NonCapturingGroup(Pattern(r"ust"), count_max=1, greedy=False)
)

# september month
september = WordBoundary(
    (Pattern(r"S") | Pattern(r"s"))
    & NonCapturingGroup(Pattern(r"ep"), count=1)
    & (NonCapturingGroup(Pattern(r"t"), count_max=1, greedy=False)
       | NonCapturingGroup(Pattern(r"tember"), count_max=1, greedy=False)
       )
)

# october month
october = WordBoundary(
    (Pattern(r"O") | Pattern(r"o"))
    & NonCapturingGroup(Pattern(r"ct"), count=1)
    & NonCapturingGroup(Pattern(r"ober"), count_max=1, greedy=False)
)

# november month
november = WordBoundary(
    (Pattern(r"N") | Pattern(r"n"))
    & NonCapturingGroup(Pattern(r"ov"), count=1)
    & NonCapturingGroup(Pattern(r"ember"), count_max=1, greedy=False)
)

# december month
december = WordBoundary(
    (Pattern(r"D") | Pattern(r"d"))
    & NonCapturingGroup(Pattern(r"ec"), count=1)
    & NonCapturingGroup(Pattern(r"ember"), count_max=1, greedy=False)
)

months_names = jan | feb | march | april | may | june | july | august | september \
               | october | november | december
months = WordBoundary(space & (months_numbers | months_names) & space)
months_names_only = WordBoundary(space & months_names & space)
years = WordBoundary(space & Pattern(r"\d", count=4, alias="YYYY") & space)

# delimiters
hyphen = NonCapturingGroup(Pattern(r"-", alias="-"), count=1)
colon = NonCapturingGroup(Pattern(r":", alias=":"), count=1)
backslash = NonCapturingGroup(Pattern(r"\/", alias="/"), count=1)
dot = NonCapturingGroup(Pattern(r"\.", alias="."), count=1)
comma = NonCapturingGroup(Pattern(r",", alias=","), count=1, greedy=False)

# European Date Format
eu_date_with_hyphen = years & hyphen & months & hyphen & ((day_numbers & day_postfix) | day_numbers)
eu_date_with_colon = years & colon & months & colon & ((day_numbers & day_postfix) | day_numbers)
eu_date_with_dot = years & dot & months & dot & ((day_numbers & day_postfix) | day_numbers)
eu_date_with_backslash = years & backslash & months & backslash & ((day_numbers & day_postfix) | day_numbers)
eu_date_with_comma = years & ((space & comma & space) | comma | space) & months_names_only & (
        (space & comma & space) | comma | space) & ((day_numbers & day_postfix) | day_numbers)
eu_date_with_space = years & space & months_names_only & ((day_numbers & day_postfix) | day_numbers)
eu_date = NamedCapturingGroup(name="eu_fmt_date",
                              pattern=(eu_date_with_colon
                                       | eu_date_with_hyphen
                                       | eu_date_with_backslash
                                       | eu_date_with_dot
                                       | eu_date_with_comma
                                       | eu_date_with_space
                                       )
                              )

# Indian Date format
ind_date_with_hyphen = ((day_numbers & day_postfix) | day_numbers) & hyphen & months & hyphen & years
ind_date_with_colon = ((day_numbers & day_postfix) | day_numbers) & colon & months & colon & years
ind_date_with_dot = ((day_numbers & day_postfix) | day_numbers) & dot & months & dot & years
ind_date_with_backslash = ((day_numbers & day_postfix) | day_numbers) & backslash & months & backslash & years
ind_date_with_comma = ((day_numbers & day_postfix) | day_numbers) & (
        (space & comma & space) | comma | space) & months_names_only & (
                              (space & comma & space) | comma | space) & years
ind_date_with_space = ((day_numbers & day_postfix) | day_numbers) & months_names_only & years
ind_date = NamedCapturingGroup(name="ind_fmt_date",
                               pattern=(ind_date_with_hyphen
                                        | ind_date_with_colon
                                        | ind_date_with_backslash
                                        | ind_date_with_dot
                                        | ind_date_with_comma
                                        | ind_date_with_space
                                        )
                               )

date_Date_dated_Dated = (Pattern("d", count=1) | Pattern("D", count=1)) \
                        & Pattern("ate") & Pattern("d", count_min=0, greedy=False)

dob = (
        (Pattern(r"d", count=1) | Pattern(r"D", count=1))
        & (dot | space) & (Pattern(r"o", count=1) | Pattern(r"O", count=1))
        & (dot | space) & (Pattern(r"b", count=1, greedy=False) | Pattern(r"B", count=1, greedy=False))
)

# times pattern
sextile_unit = SetOf(Pattern(r"0-9"), count=1)
sextile_tens = SetOf(Pattern(r"0-5"), count=1)
O_59 = WordBoundary(sextile_unit | (sextile_tens & sextile_unit))
minutes = space & NonCapturingGroup(pattern=O_59) & space
seconds = space & NonCapturingGroup(pattern=O_59) & space
hours = space & SetOf(Pattern(r"0-1"), count=1) & SetOf(Pattern(r"0-9"), count=1) \
        | Pattern(r"2", count=1) & SetOf(Pattern(r"0-3"), count=1) & space
am = WordBoundary(NonCapturingGroup(pattern=Pattern(r"am") | Pattern(r"AM"), greedy=False))
pm = WordBoundary(NonCapturingGroup(pattern=Pattern(r"pm") | Pattern(r"PM"), greedy=False))
am_or_pm = space & NamedCapturingGroup(name="am_or_pm", pattern=(am | pm)) & space
times = NamedCapturingGroup(name="times",
                            pattern=WordBoundary((
                                                         (hours & colon & minutes & colon & seconds)
                                                         | (hours & colon & minutes)
                                                         | hours) & am_or_pm
                                                 )

                            , greedy=False)

date_prefix = NamedCapturingGroup(
    name="date_prefix",
    pattern=WordBoundary(space & (date_Date_dated_Dated | dob)
                         & space & (colon | hyphen | space | colon & hyphen)
                         & space),
    greedy=False
)

optional_words = WordBoundary(space & NonCapturingGroup(Pattern(r"\w", count_min=0, greedy=False)) & space)

dates = date_prefix & optional_words & (eu_date | ind_date) & optional_words & times


def get_date(date_str):
    delimiters = (hyphen | colon | dot | backslash | space | ((space & comma & space) | comma))
    eu_y_m_d = NamedCapturingGroup("year", years) & delimiters \
               & NamedCapturingGroup("month", months) & delimiters \
               & NamedCapturingGroup("day", day_numbers) & delimiters & day_postfix

    in_d_m_y = NamedCapturingGroup("day", day_numbers) & delimiters & day_postfix & delimiters \
               & NamedCapturingGroup("month", months) & delimiters \
               & NamedCapturingGroup("year", years)

    grp_list = pp.Regex(dates.pattern, flags=IGNORECASE).scanString(date_str)

    if grp_list:  # if grp items is False skip it
        for text, start, end in grp_list:
            dt = {}
            if eu_date.name in text and any([text[eu_date.name]]):
                for txt, st, en in pp.Regex(eu_y_m_d.pattern, flags=IGNORECASE).scanString(text[eu_date.name]):
                    d = None
                    try:
                        month = int(txt["month"])
                        d = datetime(year=int(txt["year"]), month=month, day=int(txt["day"]))
                    except (Exception,):
                        try:
                            month = _monthsToNum[txt["month"][:3].lower()]
                            d = datetime(year=int(txt["year"]), month=month, day=int(txt["day"]))
                        except (Exception,):
                            pass
                    if d is not None:
                        dt.update(dict(datetime=d, **txt))

            if ind_date.name in text and any([text[ind_date.name]]):
                for txt, st, en in pp.Regex(in_d_m_y.pattern, flags=IGNORECASE).scanString(text[ind_date.name]):
                    d = None
                    try:
                        month = int(txt["month"])
                        d = datetime(year=int(txt["year"]), month=month, day=int(txt["day"]))
                    except (Exception,):
                        try:
                            month = _monthsToNum[txt["month"][:3].lower()]
                            d = datetime(year=int(txt["year"]), month=month, day=int(txt["day"]))
                        except (Exception,):
                            pass
                    if d is not None:
                        dt.update(dict(datetime=d, **txt))
            if any(dt):
                date_dict = dict(span=[start, end], **text, **dt)
                yield date_dict

# if __name__ == '__main__':
#     print(ind_date | eu_date )
#     get_date("2020/feb/29")
#     get_date("date: 2021/01/31, 20/01/2001")
#     get_date("Date: 2021/12/31, 20/12/2001")
#     get_date("dated: 2021/12/31, 20/12/2001")
#     get_date("Dated: 2021/12/31, 20/12/2001")
#     get_date("dob: 2021/12/31, 20/12/2001")
#     get_date("Dob: 2021/12/31, 20/12/2001")
#     get_date("DoB: 2021/12/31, 20/12/2001")
#     get_date("DOB: 2021/12/31, 20/12/2001")
#     get_date("d.ob: 2021/12/31, 20/12/2001")
#     get_date("D.ob: 2021/12/31, 20/12/2001")
#     get_date("D.oB: 2021/12/31, 20/12/2001")
#     get_date("D.OB: 2021/12/31, 20/12/2001")
#     get_date("do.b: 2021/12/31, 20/12/2001")
#     get_date("Do.b: 2021/12/31, 20/12/2001")
#     get_date("Do.B: 2021/12/31, 20/12/2001")
#     get_date("DO.B: 2021/12/31, 20/12/2001")
#     get_date("d.o.b: 2021/12/31, 20/12/2001")
#     get_date("D.o.b: 2021/12/31, 20/12/2001")
#     get_date("D.o.B: 2021/12/31, 20/12/2001")
#     get_date("D.O.B: 2021/12/31, 20/12/2001")
#     get_date("D.O.BB: 2021/12/31, 20/12/2001")
#     get_date("D.O.BB: 2021/03/31, 20/12/2001")
#     get_date("D.O.BB: 2021/3/31, 20/12/2001")
#     get_date("D.O.BB: 2021/13/31, 20/12/2001")
#     get_date("2021/12/31, 20/12/2001")
#     get_date("2021/12/31, 20/June/2001")
#     get_date("2021/12/31, 20/june/2001")
#     get_date("2021/12/31, 20/jun/2001")
#     date = get_date("my date will be 2021/December/31, "
#                     " 2010 Apr 20 12 am "
#                     ""
#                     "on the date 20, APr, 2001 at 12:00 pm and many "
#                     "other dates when nations were born, 20-1-2031")
#     for dat in date:
#         print(dat)
#         print(dat["datetime"].isoformat())
#     print(*pp.Regex(dates.pattern, flags=IGNORECASE).scanString("Wedding date is fixed to be 20th, Apr, 2010"))
#     print(ind_date.alias)
