# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT



import io
import logging
import logging.handlers
import os
import re
import sys
from typing import IO, List, Optional, Tuple

from typing_extensions import Final, Literal

try:
    import curses

    import _curses  # noqa

    CURSES_ENABLED = True
except ImportError:
    CURSES_ENABLED = False

# so we can't get the color code from curses.
PLAIN_ANSI_DIM = "\x1b[2m"  # type: Final

DEFAULT_SOURCE_OFFSET = 4  # type: Final
DEFAULT_COLUMNS = 80  # type: Final

# At least this number of columns will be shown on each side of
# error location when printing source code snippet.
MINIMUM_WIDTH = 20

# VT100 color code processing was added in Windows 10, but only the second major update,
# Threshold 2. Fortunately, everyone (even on LTSB, Long Term Support Branch) should
# have a version of Windows 10 newer than this. Note that Windows 8 and below are not
# supported, but are either going out of support, or make up only a few % of the market.
MINIMUM_WINDOWS_MAJOR_VT100 = 10
MINIMUM_WINDOWS_BUILD_VT100 = 10586


class ColorCodes:
    grey = "\x1b[38;21m"
    green = "\x1b[1;32m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    blue = "\x1b[1;34m"
    light_blue = "\x1b[1;36m"
    purple = "\x1b[1;35m"
    reset = "\x1b[0m"


class ColorizedArgsFormatter(logging.Formatter):
    """
    refer : https://stackoverflow.com/a/61996622
    Usage:
        root_logger = logging.getLogger()
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_format = "%(asctime)s - %(levelname)-8s - %(name)-25s - %(message)s"
        colored_formatter = ColorizedArgsFormatter(console_format)
        console_handler.setFormatter(colored_formatter)
        root_logger.addHandler(console_handler)

        logger = logging.getLogger(__name__)
        logger.info("Hello World")
        logger.info("Request from {} handled in {:.3f} ms", socket.gethostname(), 11)
        logger.info("Request from {} handled in {:.3f} ms", "127.0.0.1", 33.1)
        logger.info("My favorite drinks are {}, {}, {}, {}", "milk", "wine", "tea", "beer")
        logger.debug("this is a {} message", logging.getLevelName(logging.DEBUG))
        logger.info("this is a {} message", logging.getLevelName(logging.INFO))
        logger.warning("this is a {} message", logging.getLevelName(logging.WARNING))
        logger.error("this is a {} message", logging.getLevelName(logging.ERROR))
        logger.critical("this is a {} message", logging.getLevelName(logging.CRITICAL))
        logger.info("Does old-style formatting also work? %s it is, but no colors (yet)", True)

    """

    arg_colors = [ColorCodes.purple, ColorCodes.light_blue]
    level_fields = ["levelname", "levelno"]
    level_to_color = {
        logging.DEBUG: ColorCodes.grey,
        logging.INFO: ColorCodes.green,
        logging.WARNING: ColorCodes.yellow,
        logging.ERROR: ColorCodes.red,
        logging.CRITICAL: ColorCodes.bold_red,
    }

    def __init__(self, fmt: str):
        super().__init__()
        self.level_to_formatter = {}

        def add_color_format(level: int):
            color = ColorizedArgsFormatter.level_to_color[level]
            _format = fmt
            for fld in ColorizedArgsFormatter.level_fields:
                search = "(%\(" + fld + "\).*?s)"
                _format = re.sub(search, f"{color}\\1{ColorCodes.reset}", _format)
            formatter = logging.Formatter(_format)
            self.level_to_formatter[level] = formatter

        add_color_format(logging.DEBUG)
        add_color_format(logging.INFO)
        add_color_format(logging.WARNING)
        add_color_format(logging.ERROR)
        add_color_format(logging.CRITICAL)

    @staticmethod
    def rewrite_record(record: logging.LogRecord):
        if not BraceFormatStyleFormatter.is_brace_format_style(record):
            return

        msg = record.msg
        msg = msg.replace("{", "_{{")
        msg = msg.replace("}", "_}}")
        placeholder_count = 0
        # add ANSI escape code for next alternating color before each formatting parameter
        # and reset color after it.
        while True:
            if "_{{" not in msg:
                break
            color_index = placeholder_count % len(ColorizedArgsFormatter.arg_colors)
            color = ColorizedArgsFormatter.arg_colors[color_index]
            msg = msg.replace("_{{", color + "{", 1)
            msg = msg.replace("_}}", "}" + ColorCodes.reset, 1)
            placeholder_count += 1

        record.msg = msg.format(*record.args)
        record.args = []

    def format(self, record):
        orig_msg = record.msg
        orig_args = record.args
        formatter = self.level_to_formatter.get(record.levelno)
        self.rewrite_record(record)
        formatted = formatter.format(record)

        # restore log record to original state for other handlers
        record.msg = orig_msg
        record.args = orig_args
        return formatted


class BraceFormatStyleFormatter(logging.Formatter):
    def __init__(self, fmt: str):
        super().__init__()
        self.formatter = logging.Formatter(fmt)

    @staticmethod
    def is_brace_format_style(record: logging.LogRecord):
        if len(record.args) == 0:
            return False

        msg = record.msg
        if "%" in msg:
            return False

        count_of_start_param = msg.count("{")
        count_of_end_param = msg.count("}")

        if count_of_start_param != count_of_end_param:
            return False

        if count_of_start_param != len(record.args):
            return False

        return True

    @staticmethod
    def rewrite_record(record: logging.LogRecord):
        if not BraceFormatStyleFormatter.is_brace_format_style(record):
            return

        record.msg = record.msg.format(*record.args)
        record.args = []

    def format(self, record):
        orig_msg = record.msg
        orig_args = record.args
        self.rewrite_record(record)
        formatted = self.formatter.format(record)

        # restore log record to original state for other handlers
        record.msg = orig_msg
        record.args = orig_args
        return formatted


def split_words(msg: str) -> List[str]:
    """Split line of text into words (but not within quoted groups)."""
    next_word = ""
    res = []  # type: List[str]
    allow_break = True
    for c in msg:
        if c == " " and allow_break:
            res.append(next_word)
            next_word = ""
            continue
        if c == '"':
            allow_break = not allow_break
        next_word += c
    res.append(next_word)
    return res


def get_terminal_width() -> int:
    """Get current terminal width if possible, otherwise return the default one."""
    try:
        cols, _ = os.get_terminal_size()
    except OSError:
        return DEFAULT_COLUMNS
    else:
        if cols == 0:
            return DEFAULT_COLUMNS
        return cols


def soft_wrap(msg: str, max_len: int, first_offset: int, num_indent: int = 0) -> str:
    """Wrap a long error message into few lines.

    Breaks will only happen between words, and never inside a quoted group
    (to avoid breaking types such as "Union[int, str]"). The 'first_offset' is
    the width before the start of first line.

    Pad every next line with 'num_indent' spaces. Every line will be at most 'max_len'
    characters, except if it is a single word or quoted group.

    For example:
               first_offset
        ------------------------
        path/to/file: error: 58: Some very long error message
            that needs to be split in separate lines.
            "Long[Type, Names]" are never split.
        ^^^^--------------------------------------------------
        num_indent           max_len
    """
    words = split_words(msg)
    next_line = words.pop(0)
    lines = []  # type: List[str]
    while words:
        next_word = words.pop(0)
        max_line_len = max_len - num_indent if lines else max_len - first_offset
        # Add 1 to account for space between words.
        if len(next_line) + len(next_word) + 1 <= max_line_len:
            next_line += " " + next_word
        else:
            lines.append(next_line)
            next_line = next_word
    lines.append(next_line)
    padding = "\n" + " " * num_indent
    return padding.join(lines)


def trim_source_line(
        line: str, max_len: int, col: int, min_width: int
) -> Tuple[str, int]:
    """Trim a line of source code to fit into max_len.

    Show 'min_width' characters on each side of 'col' (an error location). If either
    start or end is trimmed, this is indicated by adding '...' there.
    A typical result looks like this:
        ...some_variable = function_to_call(one_arg, other_arg) or...

    Return the trimmed string and the column offset to to adjust error location.
    """
    if max_len < 2 * min_width + 1:
        # In case the window is too tiny it is better to still show something.
        max_len = 2 * min_width + 1

    # Trivial case: line already fits in.
    if len(line) <= max_len:
        return line, 0

    # If column is not too large so that there is still min_width after it,
    # the line doesn't need to be trimmed at the start.
    if col + min_width < max_len:
        return line[:max_len] + "...", 0

    # Otherwise, if the column is not too close to the end, trim both sides.
    if col < len(line) - min_width - 1:
        offset = col - max_len + min_width + 1
        return "..." + line[offset: col + min_width + 1] + "...", offset - 3

    # Finally, if the column is near the end, just trim the start.
    return "..." + line[-max_len:], len(line) - max_len - 3


class FancyFormatter:
    """Apply color and bold font to terminal output.

    This currently only works on Linux and Mac.
    """

    def __init__(self, f_out: IO[str], f_err: IO[str], show_error_codes: bool) -> None:
        self.show_error_codes = show_error_codes
        # Check if we are in a human-facing terminal on a supported platform.
        if sys.platform not in ("linux", "darwin", "win32"):
            self.dummy_term = True
            return
        force_color = int(os.getenv("MYPY_FORCE_COLOR", "0"))
        if not force_color and (not f_out.isatty() or not f_err.isatty()):
            self.dummy_term = True
            return
        if sys.platform == "win32":
            self.dummy_term = not self.initialize_win_colors()
        else:
            self.dummy_term = not self.initialize_unix_colors()
        if not self.dummy_term:
            self.colors = {
                "red": self.RED,
                "green": self.GREEN,
                "blue": self.BLUE,
                "yellow": self.YELLOW,
                "none": "",
            }

    def initialize_win_colors(self) -> bool:
        """Return True if initialization was successful and we can use colors, False otherwise"""
        # Windows ANSI escape sequences are only supported on Threshold 2 and above.
        # we check with an assert at runtime and an if check for mypy, as asserts do not
        # yet narrow platform
        assert sys.platform == "win32"
        if sys.platform == "win32":
            winver = sys.getwindowsversion()
            if (
                    winver.major < MINIMUM_WINDOWS_MAJOR_VT100
                    or winver.build < MINIMUM_WINDOWS_BUILD_VT100
            ):
                return False
            import ctypes

            kernel32 = ctypes.windll.kernel32
            ENABLE_PROCESSED_OUTPUT = 0x1
            ENABLE_WRAP_AT_EOL_OUTPUT = 0x2
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x4
            STD_OUTPUT_HANDLE = -11
            kernel32.SetConsoleMode(
                kernel32.GetStdHandle(STD_OUTPUT_HANDLE),
                ENABLE_PROCESSED_OUTPUT
                | ENABLE_WRAP_AT_EOL_OUTPUT
                | ENABLE_VIRTUAL_TERMINAL_PROCESSING,
            )
            self.BOLD = "\033[1m"
            self.UNDER = "\033[4m"
            self.BLUE = "\033[94m"
            self.GREEN = "\033[92m"
            self.RED = "\033[91m"
            self.YELLOW = "\033[93m"
            self.NORMAL = "\033[0m"
            self.DIM = "\033[2m"
            return True
        return False

    def initialize_unix_colors(self) -> bool:
        """Return True if initialization was successful and we can use colors, False otherwise"""
        if not CURSES_ENABLED:
            return False
        try:
            # setupterm wants a fd to potentially write an "initialization sequence".
            # We override sys.stdout for the daemon API so if stdout doesn't have an fd,
            # just give it /dev/null.
            try:
                fd = sys.stdout.fileno()
            except io.UnsupportedOperation:
                with open("/dev/null", "rb") as f:
                    curses.setupterm(fd=f.fileno())
            else:
                curses.setupterm(fd=fd)
        except curses.error:
            # Most likely terminfo not found.
            return False
        bold = curses.tigetstr("bold")
        under = curses.tigetstr("smul")
        set_color = curses.tigetstr("setaf")
        if not (bold and under and set_color):
            return False

        self.NORMAL = curses.tigetstr("sgr0").decode()
        self.BOLD = bold.decode()
        self.UNDER = under.decode()
        dim = curses.tigetstr("dim")
        # TODO: more reliable way to get gray color good for both dark and light schemes.
        self.DIM = dim.decode() if dim else PLAIN_ANSI_DIM

        self.BLUE = curses.tparm(set_color, curses.COLOR_BLUE).decode()
        self.GREEN = curses.tparm(set_color, curses.COLOR_GREEN).decode()
        self.RED = curses.tparm(set_color, curses.COLOR_RED).decode()
        self.YELLOW = curses.tparm(set_color, curses.COLOR_YELLOW).decode()
        return True

    def style(
            self,
            text: str,
            color: Literal["red", "green", "blue", "yellow", "none"],
            bold: bool = False,
            underline: bool = False,
            dim: bool = False,
    ) -> str:
        """Apply simple color and style (underlined or bold)."""
        if self.dummy_term:
            return text
        if bold:
            start = self.BOLD
        else:
            start = ""
        if underline:
            start += self.UNDER
        if dim:
            start += self.DIM
        return start + self.colors[color] + text + self.NORMAL

    def fit_in_terminal(
            self, messages: List[str], fixed_terminal_width: Optional[int] = None
    ) -> List[str]:
        """Improve readability by wrapping error messages and trimming source code."""
        width = (
                fixed_terminal_width
                or int(os.getenv("MYPY_FORCE_TERMINAL_WIDTH", "0"))
                or get_terminal_width()
        )
        new_messages = messages.copy()
        for i, error in enumerate(messages):
            if ": error:" in error:
                loc, msg = error.split("error:", maxsplit=1)
                msg = soft_wrap(msg, width, first_offset=len(loc) + len("error: "))
                new_messages[i] = loc + "error:" + msg
            if error.startswith(" " * DEFAULT_SOURCE_OFFSET) and "^" not in error:
                # TODO: detecting source code highlights through an indent can be surprising.
                # Restore original error message and error location.
                error = error[DEFAULT_SOURCE_OFFSET:]
                column = messages[i + 1].index("^") - DEFAULT_SOURCE_OFFSET

                # Let source have some space also on the right side, plus 6
                # to accommodate ... on each side.
                max_len = width - DEFAULT_SOURCE_OFFSET - 6
                source_line, offset = trim_source_line(
                    error, max_len, column, MINIMUM_WIDTH
                )

                new_messages[i] = " " * DEFAULT_SOURCE_OFFSET + source_line
                # Also adjust the error marker position.
                new_messages[i + 1] = (
                        " " * (DEFAULT_SOURCE_OFFSET + column - offset) + "^"
                )
        return new_messages

    def colorize(self, error: str) -> str:
        """Colorize an output line by highlighting the status and error code.

        If fixed_terminal_width is given, use it instead of calling get_terminal_width()
        (used by the daemon).
        """
        if ": error:" in error:
            loc, msg = error.split("error:", maxsplit=1)
            if not self.show_error_codes:
                return (
                        loc
                        + self.style("error:", "red", bold=True)
                        + self.highlight_quote_groups(msg)
                )
            codepos = msg.rfind("[")
            if codepos != -1:
                code = msg[codepos:]
                msg = msg[:codepos]
            else:
                code = ""  # no error code specified
            return (
                    loc
                    + self.style("error:", "red", bold=True)
                    + self.highlight_quote_groups(msg)
                    + self.style(code, "yellow")
            )
        elif ": note:" in error:
            loc, msg = error.split("note:", maxsplit=1)
            return loc + self.style("note:", "blue") + self.underline_link(msg)
        elif error.startswith(" " * DEFAULT_SOURCE_OFFSET):
            # TODO: detecting source code highlights through an indent can be surprising.
            if "^" not in error:
                return self.style(error, "none", dim=True)
            return self.style(error, "red")
        else:
            return error

    def highlight_quote_groups(self, msg: str) -> str:
        """Make groups quoted with double quotes bold (including quotes).

        This is used to highlight types, attribute names etc.
        """
        if msg.count('"') % 2:
            # Broken error message, don't do any formatting.
            return msg
        parts = msg.split('"')
        out = ""
        for i, part in enumerate(parts):
            if i % 2 == 0:
                out += self.style(part, "none")
            else:
                out += self.style('"' + part + '"', "none", bold=True)
        return out

    def underline_link(self, note: str) -> str:
        """Underline a link in a note message (if any).

        This assumes there is at most one link in the message.
        """
        match = re.search(r"https?://\S*", note)
        if not match:
            return note
        start = match.start()
        end = match.end()
        return (
                note[:start]
                + self.style(note[start:end], "none", underline=True)
                + note[end:]
        )

    def format_success(self, n_sources: int, use_color: bool = True) -> str:
        """Format short summary in case of success.

        n_sources is total number of files passed directly on command line,
        i.e. excluding stubs and followed imports.
        """
        msg = "Success: no issues found in {}" " source file{}".format(
            n_sources, "s" if n_sources != 1 else ""
        )
        if not use_color:
            return msg
        return self.style(msg, "green", bold=True)

    def format_error(
            self, n_errors: int, n_files: int, n_sources: int, use_color: bool = True
    ) -> str:
        """Format a short summary in case of errors."""
        msg = "Found {} error{} in {} file{}" " (checked {} source file{})".format(
            n_errors,
            "s" if n_errors != 1 else "",
            n_files,
            "s" if n_files != 1 else "",
            n_sources,
            "s" if n_sources != 1 else "",
        )
        if not use_color:
            return msg
        return self.style(msg, "red", bold=True)
