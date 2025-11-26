"""Logging configuration for the application."""

import logging
import logging.handlers
import sys
from pathlib import Path


def setup_logging(verbose: bool = False) -> None:
    """Configure application logging.

    Args:
        verbose: Enable DEBUG level logging
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Create logs directory
    log_dir = Path.home() / ".local" / "share" / "simple-analytics-viewer" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                log_dir / "app.log",
                maxBytes=10_485_760,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
        ]
    )

    # Quiet noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
