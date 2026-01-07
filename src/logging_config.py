"""
Green Bond Tracker - Logging Configuration Module

This module provides centralized logging configuration for the green bond tracker.
It supports different logging levels and formats for development and production use.

Note: This is an educational project and should not be used for investment advice.
"""

import logging
import sys

# Global logger instance
_logger: logging.Logger | None = None


def get_logger(name: str = "green_bond_tracker") -> logging.Logger:
    """
    Get or create the application logger.

    Parameters
    ----------
    name : str, optional
        Logger name. Default is "green_bond_tracker"

    Returns
    -------
    logging.Logger
        Configured logger instance
    """
    global _logger
    if _logger is None:
        _logger = logging.getLogger(name)
        # Set default level - will be overridden by setup_logging
        _logger.setLevel(logging.INFO)
    return _logger


def setup_logging(verbose: bool = False, quiet: bool = False) -> None:
    """
    Configure application-wide logging.

    Parameters
    ----------
    verbose : bool, optional
        If True, enable DEBUG level logging. Default is False
    quiet : bool, optional
        If True, suppress INFO logs (show WARN/ERROR only). Default is False

    Notes
    -----
    - Logs are sent to stdout for easy redirection
    - Format: timestamp, level, message
    - Stack traces are shown in DEBUG mode only
    """
    logger = get_logger()

    # Clear any existing handlers to avoid duplicate logs
    logger.handlers.clear()

    # Determine log level
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger.setLevel(level)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create formatter with timestamp, level, and message
    if verbose:
        # More detailed format for debugging
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # Cleaner format for normal use
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    if verbose:
        logger.debug("Logging initialized in DEBUG mode")
    elif quiet:
        logger.debug("Logging initialized in QUIET mode (WARNING+ only)")
    else:
        logger.debug("Logging initialized in INFO mode")


def log_exception(
    logger: logging.Logger,
    message: str,
    exception: Exception,
    verbose: bool = False,
) -> None:
    """
    Log an exception with appropriate detail level.

    Parameters
    ----------
    logger : logging.Logger
        Logger instance to use
    message : str
        Human-readable error message
    exception : Exception
        Exception object
    verbose : bool, optional
        If True, include full stack trace. Default is False

    Notes
    -----
    In verbose mode, full stack traces are shown.
    In normal mode, only the error message is shown.
    """
    if verbose or logger.level == logging.DEBUG:
        logger.error(message, exc_info=True)
    else:
        logger.error(f"{message}: {exception}")


def format_validation_error(column: str | None, message: str, suggestion: str | None = None) -> str:
    """
    Format a validation error message consistently.

    Parameters
    ----------
    column : str or None
        Column name where the error occurred
    message : str
        Description of the error
    suggestion : str, optional
        Actionable suggestion for fixing the error

    Returns
    -------
    str
        Formatted error message
    """
    parts = []
    if column:
        parts.append(f"Column '{column}':")
    parts.append(message)
    if suggestion:
        parts.append(f"→ {suggestion}")
    return " ".join(parts)
