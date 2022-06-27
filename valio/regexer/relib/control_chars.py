# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT



from valio.regexer.regexps import Pattern, SetOf

null_byte = Pattern(pattern=r"\x00")
start_heading = Pattern(pattern=r"\x01")
start_text = Pattern(pattern=r"\x02")
end_text = Pattern(pattern=r"\x03")
end_transmission = Pattern(pattern=r"\x04")
enquiry = Pattern(pattern=r"\x05")
acknowledge = Pattern(pattern=r"\x06")
ring_terminal_bell = Pattern(pattern=r"\x07")
backspace = Pattern(pattern=r"\x08")

x00_to_x08_range = (
        start_heading
        & start_text
        & end_text
        & end_transmission
        & enquiry
        & acknowledge
        & ring_terminal_bell
        & backspace
)

x00_to_x08_set = SetOf(x00_to_x08_range)
x00_x08_range = Pattern(pattern=fr"{start_heading}-{backspace}")
x00_x08_set = SetOf(x00_x08_range)

# Line Chars
horizontal_tab = Pattern(pattern=r"\x09")
line_feed = Pattern(pattern=r"\x0a")
vertical_tab = Pattern(pattern=r"\x0b")
form_feed = Pattern(pattern=r"\x0c")
carriage_return = Pattern(pattern=r"\x0d")
shift_out = Pattern(pattern=r"\x0e")
shift_in = Pattern(pattern=r"\x0F")
data_link_escape = Pattern(pattern=r"\x10")
device_control_1 = Pattern(pattern=r"\x11")
device_control_2 = Pattern(pattern=r"\x12")
device_control_3 = Pattern(pattern=r"\x13")
device_control_4 = Pattern(pattern=r"\x14")
negative_acknowledge = Pattern(pattern=r"\x15")
synchronous_idle = Pattern(pattern=r"\x16")
end_of_transmission_block = Pattern(pattern=r"\x17")
cancel = Pattern(pattern=r"\x18")
end_of_medium = Pattern(pattern=r"\x19")
substitute_character = Pattern(pattern=r"\x1a")
escape = Pattern(r"\x1b")
file_separator = Pattern(pattern=r"\x1c")
group_separator = Pattern(pattern=r"\x1d")
record_separator = Pattern(pattern=r"\x1e")
unit_separator = Pattern(pattern=r"\x1f")

x09_to_x1f_rage = (
        horizontal_tab
        & line_feed
        & vertical_tab
        & form_feed
        & carriage_return
        & shift_out
        & shift_in
        & data_link_escape
        & device_control_1
        & device_control_2
        & device_control_3
        & device_control_4
        & negative_acknowledge
        & synchronous_idle
        & end_of_transmission_block
        & cancel
        & end_of_medium
        & substitute_character
        & escape
        & file_separator
        & group_separator
        & record_separator
        & unit_separator
)
x09_to_x1f_set = SetOf(x09_to_x1f_rage)
x09_x1f_range = Pattern(pattern=fr"{horizontal_tab}-{unit_separator}")
x09_x1f_set = SetOf(x09_x1f_range)
