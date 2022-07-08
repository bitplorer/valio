# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""Information about PAN-Card.
    reference: https://stackoverflow.com/a/17684642
    1) The first three letters are sequence of alphabets from AAA to zzz
    2) The fourth character informs about the type of holder of the Card. Each assesse is unique:`
    
        C — Company
        P — Person
        H — HUF(Hindu Undivided Family)
        F — Firm
        A — Association of Persons (AOP)
        T — AOP (Trust)
        B — Body of Individuals (BOI)
        L — Local Authority
        J — Artificial Judicial Person
        G — Government
    
    
    3) The fifth character of the PAN is the first character
        (a) of the surname / last name of the person, in the case of 
    a "Personal" PAN card, where the fourth character is "P" or
        (b) of the name of the Entity/ Trust/ Society/ Organisation
    in the case of Company/ HUF/ Firm/ AOP/ BOI/ Local Authority/ Artificial Jurdical Person/ Govt,
    where the fourth character is "C","H","F","A","T","B","L","J","G".
    
    4) The last character is a alphabetic check digit.
    PAN Card uses Luhn Mod 26 for correctness check.
"""

import re

from valio.regexer.regexps import Pattern, WordBoundary

A_Z = list(chr(i) for i in range(65, 65 + 26))
A_Z_MAP = dict(zip(A_Z, range(1, 26)))

__all__ = ["is_valid_pan_number"]

decimal_decoder = lambda s: int(s) if s not in A_Z_MAP else A_Z_MAP[s]
decimal_encoder = lambda i: str(i)


def luhn_sum_mod_base(string, base=10, decoder=decimal_decoder):
    # Adapted from http://en.wikipedia.org/wiki/Luhn_algorithm
    digits = list(map(decoder, string))
    return (sum(digits[::-2]) +
            sum(list(map(lambda d: sum(divmod(2 * d, base)), digits[-2::-2])))) % base


def generate(string, base=10, encoder=decimal_encoder,
             decoder=decimal_decoder):
    """
    Calculates the Luhn mod N check character for the given input string. This
    character should be appended to the input string to produce a valid Luhn
    mod N string in the given base.
    >>> value = '4205092350249'
    >>> generate(value)
    '1'
    When operating in a base other than decimal, encoder and decoder callables
    should be supplied. The encoder should take a single argument, an integer,
    and return the character corresponding to that integer in the operating
    base. Conversely, the decoder should take a string containing a single
    character and return its integer value in the operating base. Note that
    the mapping between values and characters defined by the encoder and
    decoder should be one-to-one.
    For example, when working in hexadecimal:
    >>> hex_alphabet = '0123456789abcdef'
    >>> hex_encoder = lambda i: hex_alphabet[i]
    >>> hex_decoder = lambda s: hex_alphabet.index(s)
    >>> value = 'a8b56f'
    >>> generate(value, base=16, encoder=hex_encoder, decoder=hex_decoder)
    'b'
    >>> verify('a8b56fb', base=16, decoder=hex_decoder)
    True
    >>> verify('a8b56fc', base=16, decoder=hex_decoder)
    False
    """

    d = luhn_sum_mod_base(string + encoder(0), base=base, decoder=decoder)
    if d != 0:
        d = base - d
    return encoder(d)


def verify(string, base=10, decoder=decimal_decoder):
    """
    Verifies that the given string is a valid Luhn mod N string.
    >>> verify('5105105105105100') # MasterCard test number
    True
    When operating in a base other than decimal, encoder and decoder callables
    should be supplied. The encoder should take a single argument, an integer,
    and return the character corresponding to that integer in the operating
    base. Conversely, the decoder should take a string containing a single
    character and return its integer value in the operating base. Note that
    the mapping between values and characters defined by the encoder and
    decoder should be one-to-one.
    For example, 'b' is the correct check character for the hexadecimal string
    'a8b56f':
    >>> hex_decoder = lambda s: '0123456789abcdef'.index(s)
    >>> verify('a8b56fb', base=16, decoder=hex_decoder)
    True
    Any other check digit (in this example: 'c'), will result in a failed
    verification:
    >>> verify('a8b56fc', base=16, decoder=hex_decoder)
    False
    """

    return luhn_sum_mod_base(string, base=base, decoder=decoder) == 0


def is_valid_pan_number(par):
    re_exp = WordBoundary(Pattern(r"[A-Z]{3}[ABCFGHLJPTK]{1}[A-Z]{1}[0-9]{4}[A-Z]{1}"))
    return any(re.findall(re_exp.pattern, par))
