import os
import re
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from functools import partial
from pathlib import Path

from loguru import logger

from . import __version__ as VERSION
from .log import setup_logging
from .pkg_info import OUTPUT_FORMATS, show_package_info

HELP_FORMATTER = ArgumentDefaultsHelpFormatter


def parse_args() -> Namespace:
    parser = ArgumentParser("pkg-info", formatter_class=HELP_FORMATTER)
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("-v", "--verbose", action="count", help="Log more (-v info, -vv debug, -vv trace)", default=0)
    parser.add_argument(
        "-l",
        "--log-root",
        help="Log root path (specify '' to suppress logging to a file)",
        type=lambda s: Path(s) if s else None,
        metavar="PATH",
        default="",
    )
    parser.add_argument(
        "-t",
        "--max-workers",
        help="Max number of threads to run",
        type=int,
        metavar="N",
        default=max(1, os.cpu_count()/2),
    )
    parser.add_argument(
        "INCLUDE",
        help="Show only packages matching this regex (case insensitive)",
        type=partial(re.compile, flags=re.IGNORECASE),
        metavar="PYTHON_REGEX",
        nargs="?",
    )
    parser.add_argument(
        "-f",
        "--output-format",
        help="Output format",
        choices=OUTPUT_FORMATS,
        default="tsv",
    )

    return parser.parse_args()


def cli() -> None:
    args = parse_args()
    print(args)
    setup_logging(args)
    logger.debug("args={}", args)
    show_package_info(args)
