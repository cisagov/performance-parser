#!/usr/bin/env python

"""perf-parse converts DHS performance forms into CSV files.

Usage:
  perf_parse [--log-level=LEVEL] <form-txt> <out-csv>
  perf_parse (-h | --help)

Options:
  -h --help              Show this message.
  --log-level=LEVEL      If specified, then the log level will be set to
                         the specified value.  Valid values are "debug", "info",
                         "warning", "error", and "critical". [default: warning]
"""

import logging
import re
import sys

import docopt
import csv

from ._version import __version__

core_comp_re = re.compile("^CORE COMPETENCY (.+)$")
ach_expectations_re = re.compile("^Achieved Expectations (.+)$")
ach_excellence_re = re.compile(
    "^Achieved Excellence Additions at the Achieved Excellence level: (.+)$"
)
FIELDS = (
    "Core Competency",
    "Achievement Level",
    "Performance Standards",
    "Status Evidence/Excuse",
)


def parse(in_filename):
    """Parse the form text file."""
    results = []
    with open(in_filename, encoding="utf8") as f:
        for line in f.readlines():
            # find a core compentency
            match = core_comp_re.match(line)
            if match:
                core_comp = match.group(1)
                continue
            match = ach_expectations_re.match(line)
            if match:
                level = "3 - Achieved Expectations"
                measures = [x.strip() for x in match.group(1).split(".")][:-1]
                for m in measures:
                    results.append((core_comp, level, m + ".", ""))
                continue
            match = ach_excellence_re.match(line)
            if match:
                level = "5 - Achieved Excellence"
                measures = [x.strip() for x in match.group(1).split(".")][:-1]
                for m in measures:
                    results.append((core_comp, level, m + ".", ""))
                continue
    return results


def write_csv(fields, data, output_filename, delimiter=","):
    """Write a CVS file out."""
    csv_writer = csv.writer(open(output_filename, "w"), fields, delimiter=delimiter)
    csv_writer.writerow(FIELDS)
    for row in data:
        csv_writer.writerow(row)


def main():
    """Set up logging and call the perf_parse function."""
    args = docopt.docopt(__doc__, version=__version__)
    # Set up logging
    log_level = args["--log-level"]
    try:
        logging.basicConfig(
            format="%(asctime)-15s %(levelname)s %(message)s", level=log_level.upper()
        )
    except ValueError:
        logging.critical(
            f'"{log_level}" is not a valid logging level.  Possible values '
            "are debug, info, warning, and error."
        )
        return 1

    data = parse(args["<form-txt>"])
    write_csv(FIELDS, data, args["<out-csv>"])

    # Stop logging and clean up
    logging.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
