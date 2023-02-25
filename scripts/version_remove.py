#!/usr/bin/env python3
"""JSON Version remover."""

import json
from sys import argv


def version_removal(remove_from):
    """Remove version key from input file."""

    try:
        json_file = open(remove_from, "r")
        data = json.load(json_file)

        if "version" not in data:
            print(f"No version in {remove_from}")
            return

        del data["version"]

    except FileNotFoundError:
        print(f"File {remove_from} not found")
        return

    json_file = open(remove_from, "w")
    json_file.write(json.dumps(data, indent=2))


if not argv[1]:
    print("Use correct syntax")
    raise Exception

version_removal(argv[1])
