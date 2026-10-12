"""
Command line entry point
"""

import argparse
import sys
from typing import List, Optional

from kgi_example_queries.harvest import harvest


def main(argv: Optional[List[str]] = None) -> int:
    """
    command line entry point

    Args:
        argv: the command line arguments, sys.argv[1:] when None

    Returns:
        the process exit code
    """
    parser = argparse.ArgumentParser(prog="kgi-queries")
    parser.add_argument("command", choices=["harvest"])
    parser.parse_args(argv)
    exit_code = harvest()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
