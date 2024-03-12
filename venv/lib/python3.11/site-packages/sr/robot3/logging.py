import functools
import logging
import sys
from typing import Callable, Optional, TypeVar, Union, overload

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec
Param = ParamSpec("Param")
RetType = TypeVar("RetType")

E = TypeVar("E", bound=BaseException)

# Add a TRACE level to logging, below DEBUG
TRACE = 5


def add_trace_level() -> None:
    """Set logging to label messages at level 5 as "TRACE"."""
    logging.addLevelName(TRACE, "TRACE")


def setup_logging(debug_logging: bool, trace_logging: bool) -> None:
    """
    Set up logging for the program.

    The logging level is set to INFO by default, but can be set to DEBUG or TRACE.
    This set on the root logger, so all loggers will inherit this level.

    Logs are output to the console, with the format:
    <logger name> - <log level> - <message>

    :param debug_logging: Enable debug level logging output to the console.
    :param trace_logging: Enable trace level logging output to the console.
    """
    logformat = '%(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt=logformat)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    if not len(root_logger.handlers):
        # only add a handler if there were no handlers previously attached
        root_logger.addHandler(handler)

    if trace_logging:
        # Trace level is below debug, so debug logs will still be shown
        root_logger.setLevel(TRACE)
        logging.log(TRACE, "Trace Mode is enabled")
    elif debug_logging:
        root_logger.setLevel(logging.DEBUG)
        logging.debug("Debug Mode is enabled")
    else:
        root_logger.setLevel(logging.INFO)


@overload
def log_to_debug(
    func: None = None, *, setter: bool = False,
) -> Callable[[Callable[Param, RetType]], Callable[Param, RetType]]:
    ...


@overload
def log_to_debug(func: Callable[Param, RetType]) -> Callable[Param, RetType]:
    ...


def log_to_debug(
    func: Optional[Callable[Param, RetType]] = None, *, setter: bool = False,
) -> Union[
    Callable[[Callable[Param, RetType]], Callable[Param, RetType]],
    Callable[Param, RetType],
]:
    """
    Wrap a function to log its arguments and return value at DEBUG level.

    Logging is to the function's module logger.

    :param func: A function to wrap in debug logging
    :param setter: Whether the function is a getter (i.e. returns no value)
    :return: The wrapped function
    """

    def arg_wrapper(_func: Callable[Param, RetType]) -> Callable[Param, RetType]:
        logger = logging.getLogger(_func.__module__)

        @functools.wraps(_func)
        def wrapper_debug(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)

            if setter:
                logger.debug(f"Calling setter {_func.__qualname__}({signature})")
            else:
                logger.debug(f"Calling {_func.__qualname__}({signature})")
            value = _func(*args, **kwargs)
            if not setter:
                logger.debug(f"{_func.__qualname__!r} returned {value!r}")

            return value

        return wrapper_debug

    if func is None:
        return arg_wrapper
    else:
        return arg_wrapper(func)
