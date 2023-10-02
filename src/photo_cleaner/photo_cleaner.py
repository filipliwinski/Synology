# Copyright (c) Filip Liwiński
# Licensed under the MIT License. See the LICENSE file in the project root for license information.

"""Removes hidden files from the provieded location."""
import argparse
from datetime import datetime, timedelta
import logging
import os
import sys


from version import __version__

SCRIPT_CODE_NAME = "photo_cleaner"
SCRIPT_DESCRIPTION = "This script removes hidden files and folders."
SCRIPT_NAME = f"Photo Cleaner v.{__version__}"

START_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE_NAME = f"{SCRIPT_CODE_NAME}_{START_TIMESTAMP}.log"

logger = logging.getLogger(SCRIPT_CODE_NAME)
logger.setLevel(logging.DEBUG)

log_handler = logging.FileHandler(LOG_FILE_NAME)
log_handler.setLevel(logging.DEBUG)
logger.addHandler(log_handler)


def _delete_items(items_to_remove, dry_run):
    """Deletes items from disk."""

    for item in items_to_remove:
        if dry_run:
            logger.info("Deleted %s [dry ryn]", item)
        else:
            os.remove(item)
            logger.info("Deleted %s", item)


def _should_be_removed(full_path, item_age_in_hours):
    """Checks if an item should be removed, based on its last modification date."""

    current_datetime = datetime.now()
    last_modified_datetime = datetime.fromtimestamp(os.path.getmtime(full_path))

    should_be_removed = False

    if last_modified_datetime + timedelta(hours=item_age_in_hours) < current_datetime:
        should_be_removed = True

    logger.info("%s - %s", full_path, should_be_removed)

    return should_be_removed


def _find_items_to_remove(photos_location, max_age_in_hours):
    """Finds items to remove."""

    items_to_remove = list()

    for root, directories, files in os.walk(photos_location):

        logger.debug(root)

        for directory in directories:
            if directory[0] == ".":
                full_path = os.path.join(root, directory)
                if _should_be_removed(full_path, max_age_in_hours):
                    items_to_remove.append(full_path)

        for file in files:
            if file[0] == ".":
                full_path = os.path.join(root, file)
                if items_to_remove.count(root) == 0:
                    if _should_be_removed(full_path, max_age_in_hours):
                        items_to_remove.append(full_path)

    return items_to_remove


def main():
    """Validates arguments and executes the script."""

    logger.info(SCRIPT_NAME)
    print(SCRIPT_NAME)

    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME, description=SCRIPT_DESCRIPTION)
    parser.add_argument("-p", "--photos_location",
                        help="The location of Synology Photos folder.")
    parser.add_argument("-d", "--dry_run",
                        help="Enables dry run.", action="store_true")

    args = parser.parse_args()
    photos_location = args.photos_location
    dry_run = args.dry_run

    # Validate arguments
    if not os.path.isdir(photos_location):
        sys.exit(f"{photos_location} is not a valid directory.")

    items_to_remove = _find_items_to_remove(photos_location, 1)
    _delete_items(items_to_remove, dry_run)


if __name__ == "__main__":
    main()
