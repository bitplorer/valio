# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import logging
import os
import pathlib
import sys
import typing
from dataclasses import dataclass

__all__ = ["Logger", "LOGGER", "LOG_LEVEL", "LOG_DIR"]

LOGGER = typing.Union[bool, logging.Logger, None]
LOG_LEVEL = typing.Union[ 
    str, 
    int, 
    typing.List[str], 
    typing.List[int], 
    list[typing.Union[str, int, None]],
    None
    ]
LOG_DIR = typing.Union[str, bytes, pathlib.Path, None]


@dataclass
class Logger(object):
    _stream = False
    _nameToLevel = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "FATAL": logging.FATAL,
    }
    _levelToName = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
        logging.FATAL: "FATAL",
    }

    default_format = (
        "%(asctime)-25s:%(module)-15s:%(levelname)-8s:"
        "%(name)-45s:%(funcName)-25s:%(message)s"
    )
    default_log_dir = "logs"
    default_err_format = (
        "%(asctime)-25s:%(module)-15s:%(levelname)-8s:"
        "%(name)-45s:%(funcName)-25s:line-%(lineno)-6s:%(message)s"
    )

    logger: LOGGER = None
    log_levels: LOG_LEVEL = None
    log_dir: LOG_DIR = None

    def __init__(
            self,
            logger: LOGGER = None,
            log_levels: LOG_LEVEL = None,
            log_dir: LOG_DIR = None,
            **kwargs
    ):

        # check logger
        logger_err_msg = TypeError(
            f"expect logger to be a bool or {str(logging.Logger)} type, "
            f"got {type(logger).__name__} type instead"
        )

        if logger is not None and not isinstance(logger, (bool, logging.Logger)):
            raise logger_err_msg

        # check log_levels
        expected_levels = [*self._nameToLevel, *self._levelToName]

        def log_levels_err_msg(unexpected_typ):
            return TypeError(
                f"expect log_levels to be any of {expected_levels} "
                f"or its list, got {unexpected_typ} instead"
            )

        log_levels = (
            [log_levels] if not isinstance(log_levels, (list, tuple)) else log_levels
        )

        unexpected_levels = [
            level
            for level in log_levels
            if not isinstance(level, str) or level not in expected_levels
        ]

        if any(unexpected_levels):
            raise log_levels_err_msg(unexpected_levels)

        # check log_dir
        log_dir_err_msg = TypeError(
            f"expect dir to be a str, bytes or {str(pathlib.Path)} type, "
            f"got {type(log_dir).__name__} type instead"
        )

        if log_dir is not None and not isinstance(log_dir, (str, bytes, pathlib.Path)):
            raise log_dir_err_msg

        # assign
        self.logger = logger
        self.log_levels = log_levels

        curr_dir = os.path.abspath(os.getcwd())
        self.log_dir = (
            os.path.join(
                curr_dir,
                log_dir.decode()
                if isinstance(log_dir, bytes)
                else log_dir or self.default_log_dir,
            )
            if log_dir is not isinstance(log_dir, pathlib.Path)
            else log_dir.joinpath(self.default_log_dir)  # type: ignore
        )
        self._stream = kwargs.pop("stream", self._stream)
        self.kwargs = kwargs

    def get_record_dir(self, folder_name):
        folder_path = (
            os.path.join(self.log_dir, folder_name)
            if not isinstance(self.log_dir, pathlib.Path)
            else self.log_dir.joinpath(folder_name)
        )
        if not isinstance(folder_path, pathlib.Path):
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
        else:
            folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path

    def get_logger(self, subdir=None, record_prefix=None):
        if self.logger is None or True:
            module_name = os.path.splitext(
                os.path.basename(sys.modules["__main__"].__file__)
            )[0]
            class_name = (
                type(self).__name__
                if subdir is None
                else os.path.splitext(os.path.basename(subdir))[0]
            )
            logger = logging.getLogger(f"{module_name}.{class_name}.{record_prefix}")

            formatter = logging.Formatter(self.default_format)
            err_formatter = logging.Formatter(self.default_err_format)
            logger.setLevel(logging.DEBUG)

            if record_prefix is None:
                record_prefix = class_name

            levels = self.log_levels = (
                self.log_levels if any(self.log_levels) else list(self._nameToLevel)
            )
            levels = [
                level.lower()
                if level not in self._levelToName
                else self._levelToName[level].lower()
                for level in levels
                if level is not None
            ]
            for level in levels:
                lvl_dir = (
                    os.path.join(module_name, level)
                    if subdir is None
                    else os.path.join(os.path.join(module_name, subdir), level)
                )
                level_dir = self.get_record_dir(lvl_dir)
                record_name = f"{record_prefix}.log"
                level_record = (
                    os.path.join(level_dir, record_name)
                    if not isinstance(level_dir, pathlib.Path)
                    else level_dir.join(record_name)
                )
                level_formatter = (
                    formatter if level not in ["critical", "error"] else err_formatter
                )
                level_handler = logging.FileHandler(level_record)
                level_handler.setFormatter(level_formatter)
                level_handler.setLevel(self._nameToLevel[level.upper()])
                logger.addHandler(level_handler)
                if self._stream:
                    stream_handler = logging.StreamHandler()
                    stream_handler.setFormatter(level_formatter)
                    stream_handler.setLevel(self._nameToLevel[level.upper()])
                    logger.addHandler(stream_handler)

            self.logger = logger
        return self.logger
