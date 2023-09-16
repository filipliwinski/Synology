# Copyright (c) Filip Liwiński
# Licensed under the MIT License. See the LICENSE file in the project root for license information.

"""Removes hidden files from the provieded location."""
import argparse
from datetime import datetime
import logging
import os
import sys

from version import __version__

SCRIPT_CODE_NAME = "photo_cleaner"
SCRIPT_DESCRIPTION = "This script removes files stored in hidden folders."
SCRIPT_NAME = f"Photo Cleaner v.{__version__}"

def _cleanup_photos(photos_location, dry_run):
    """"""

    directories = os.walk(photos_location)

    for directory in directories:
        # Get the last part of the path
        target_folder = directory[0].split("\\")[-1]
        print(directory[0])

        # Identify hidden folders
        if target_folder[0] == ".":
            print(f"{target_folder} [{directory[0]}]")

            # Get files in directory
            files = directory[2]
            print(files)

            for file in files:
                if file.lower().endswith(".jpg") or file.lower().endswith(".jpeg"):
                    print(file)

def main():
    """Validates arguments and executes the script."""

    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logging.basicConfig(
        level=logging.DEBUG,
        filename=f"{SCRIPT_CODE_NAME}_{current_timestamp}.log",
        filemode="w")

    logging.info(SCRIPT_NAME)
    print(SCRIPT_NAME)

    parser = argparse.ArgumentParser(prog=SCRIPT_NAME, description=SCRIPT_DESCRIPTION)
    parser.add_argument("-p", "--photos_location", help="The location of Synology Photos folder.")
    parser.add_argument("-d", "--dry_run", help="Enables dry run.", action="store_true")

    args = parser.parse_args()
    photos_location = args.photos_location
    dry_run = args.dry_run

    # Validate arguments
    if not os.path.isdir(photos_location):
        sys.exit(f"{photos_location} is not a valid directory.")

    _cleanup_photos(photos_location, dry_run)

if __name__ == "__main__":
    main()
