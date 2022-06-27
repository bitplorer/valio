# Copyright (c) 2022 Valio
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT



class SetPropertyError(AttributeError):
    pass


class GetPropertyError(AttributeError):
    pass


class DeletePropertyError(AttributeError):
    pass


class SetAttributeError(AttributeError):
    pass


class GetAttributeError(AttributeError):
    pass


class DeleteAttributeError(AttributeError):
    pass


class DustBaseException(Exception):
    """Base Dust exception"""

    def __init__(self, error_message=None):
        super(DustBaseException, self).__init__(error_message)


class DustError(DustBaseException):
    """helper for validation parsing"""

    def __init__(self, error_message=None, error_param=None, log_message=None):
        # error_message api provides custom error message for value error
        self._error_message = None

        # error_param api provides error parameters
        self._error_param = None

        # log_message api provides a way to log messages
        self._log_message = None

        # input errors
        self._error_message_error = TypeError(
            f"expect 'message' to be '{str.__name__}' type, "
            f"got '{type(error_message).__name__}' type instead"
        )

        self._error_param_error = TypeError(
            f"expect 'param' parameter to be '{tuple.__name__}' type, "
            f"got '{type(error_param)}' type instead"
        )

        self._log_message_error = TypeError(
            f"expect 'log' to be '{str.__name__}' type, "
            f"got '{type(error_message).__name__}' type instead"
        )
        self.message = error_message
        self.param = error_param
        self.log = log_message

        super(DustError, self).__init__(self.message)

    @property
    def message(self):
        if all([self._error_message, self._error_param]):
            return self._error_message % self._error_param
        return self._error_message

    @message.setter
    def message(self, error_message=None):
        if error_message is not None and self._error_message is None:
            if not isinstance(error_message, str):
                raise self._error_message_error
            self._error_message = error_message

    @property
    def param(self):
        return self._error_param

    @param.setter
    def param(self, error_param):
        if error_param is not None and self._error_param is None:
            if not isinstance(error_param, (tuple, list)):
                raise self._error_param_error
            self._error_param = error_param

    @property
    def log(self):
        return self._log_message

    @log.setter
    def log(self, log_message):
        if log_message is not None and self._log_message is None:
            if not isinstance(log_message, str):
                raise self._log_message_error
        self._log_message = log_message
