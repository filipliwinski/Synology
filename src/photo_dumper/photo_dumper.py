# Copyright (c) Filip Liwiński
# Licensed under the MIT License. See the LICENSE file in the project root for license information.

"""Allows to copy photos from a local directory to Synology Photos."""
import os
import shutil
import sys
import logging
from datetime import datetime
import piexif

from tqdm import tqdm
from version import __version__


class FileStats:
    """
    Collects statistics of file operations.
    """

    def __init__(self, total):
        self.total = total
        self.skipped = 0
        self.conflicts = 0
        self.duplicates = 0
        self.unsupported = 0

    @property
    def total(self):
        """Returns the total number of files."""
        return self.total

    @property
    def copied(self):
        """Returns the number of copied files."""
        return self.total - self.skipped

    @property
    def skipped(self):
        """Returns the number of skipped files."""
        return self.skipped

    @property
    def conflicts(self):
        """Returns the number of files with name conflicts."""
        return self.conflicts

    @property
    def duplicates(self):
        """Returns the number of duplicated files."""
        return self.duplicates

    @property
    def unsupported(self):
        """Returns the number of unsupported files."""
        return self.unsupported

    def report_skipped(self):
        """Increments the number of skipped files."""
        self.skipped += 1

    def report_conflict(self):
        """Increments the number of files with name conflicts."""
        self.conflicts += 1
        self.report_skipped()

    def report_duplicate(self):
        """Increments the number of duplicated files."""
        self.duplicates += 1
        self.report_skipped()

    def report_unsupported(self):
        """Increments the number of unsupported files."""
        self.unsupported += 1
        self.report_skipped()

    def __str__(self):
        return f"""
        COPIED: {self.copied}
        DUPLICATES: {self.duplicates}
        CONFLICTS: {self.conflicts}
        UNSUPPORTED: {self.unsupported}"""


def _get_original_date_taken(photo_file_path):
    """
    Retrieves the creation date of the photo from the EXIF metadata. 
    If the EXIF data is not present returns the last modified date.
    """

    # Load the EXIF data from the file
    exif_data = piexif.load(photo_file_path)

    # Get the value of the DateTimeOriginal tag (0x9003) from the EXIF data
    date_taken = exif_data["Exif"].get(0x9003)

    # If the tag is present, convert the value to a datetime object and return it
    if date_taken:
        date_taken_str = date_taken.decode("utf-8")
        return datetime.strptime(date_taken_str, "%Y:%m:%d %H:%M:%S")

    # If the tag is not present or is invalid, return last modified date
    last_modified = os.path.getmtime(photo_file_path)
    return datetime.fromtimestamp(last_modified)


def _check_file_uniqueness(file_path, destination_file_path):
    """
    Returns True if the file is not a duplicate and a file with a given name
    does not exist in the target location. If the file is a duplicate, returns False
    and if a file with the given name already exists, returns None.

    Uses file size to determine uniqueness.
    """

    if not os.path.isfile(destination_file_path):
        # The file is not a duplicate
        return True

    desctination_file_size = os.path.getsize(destination_file_path)
    file_size = os.path.getsize(file_path)

    if desctination_file_size == file_size:
        # The file is a duplicate
        return False

    # The file is not a duplicate, but the file with a given name already exists
    return None


def _copy_files(source_directory, target_directory, dry_run):
    """Copies files from the provided source directory to the target directory."""

    directories = os.walk(source_directory)

    for directory in directories:
        # Check if directory should be excluded

        # Get the last part of the path
        source_folder = directory[0].split("\\")[-1]
        source_folder_path = directory[0]
        if len(source_folder) > 0 and source_folder[0] == ".":
            logging.info("%s skipped (hidden folder).", source_folder_path)
            continue

        # Get files in directory
        files = directory[2]
        if len(files) > 0:
            file_stats = FileStats(len(files))
            with tqdm(total=len(files),
                      desc=f"{source_folder_path} ({file_stats.skipped} skipped)") as pbar:
                for file in files:
                    source_file_path = f"{source_folder_path}\\{file}"

                    # Skip unsupported files
                    if not (file.lower().endswith(".jpg") or file.lower().endswith(".jpeg")):
                        logging.info(
                            "%s skipped (unsupported file type)", source_file_path)
                        file_stats.report_unsupported()
                    else:
                        creation_date = _get_original_date_taken(
                            source_file_path)
                        target_folder = creation_date.strftime("%Y\\%m")
                        target_folder_path = f"{target_directory}\\{target_folder}"

                        source_file_size = os.path.getsize(source_file_path)
                        target_file_name = (
                            f"IMG_{creation_date.strftime('%Y%m%d')}_"
                            f"{creation_date.strftime('%H%M%S')}_"
                            f"{source_file_size:08d}.JPG")
                        target_file_path = f"{target_folder_path}\\{target_file_name}"
                        is_unique = _check_file_uniqueness(
                            source_file_path, target_file_path)

                        if is_unique is None:
                            # The file is unique, but a different one with the same name exists
                            file_stats.report_conflict()
                            logging.warning("%s skipped (conflict - a file with this name already exists)",
                                            source_file_path)
                        else:
                            if is_unique:
                                # This is a new file
                                if not dry_run:
                                    if not os.path.exists(target_folder_path):
                                        os.makedirs(
                                            target_folder_path, exist_ok=True)
                                    shutil.copyfile(
                                        source_file_path, target_file_path)
                                logging.info("%s copied to %s",
                                             source_file_path, target_file_path)

                            else:
                                # The file is a duplicate
                                file_stats.report_duplicate()
                                logging.info(
                                    "%s skipped (duplicate)", source_file_path)
                    pbar.set_description(
                        f"{source_folder_path} ({file_stats.skipped} skipped)")
                    pbar.update(1)

            logging.info("""Operation summary for %s: %s""",
                         source_folder_path, file_stats)


def main():
    """Validates arguments and executes the script."""

    if len(sys.argv) < 3:
        sys.exit("Expected arguments: source_directory, target_directory")

    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logging.basicConfig(
        level=logging.DEBUG,
        filename=f"photo_dumper_{current_timestamp}.log",
        filemode="w")

    logging.info("Photo Dumper v.%s", __version__)

    source_directory = sys.argv[1]
    target_directory = sys.argv[2]
    dry_run = False

    # Validate arguments
    if not os.path.isdir(source_directory):
        sys.exit(f"{source_directory} is not a valid directory.")

    if not os.path.isdir(target_directory):
        sys.exit(f"{target_directory} is not a valid directory.")

    if dry_run:
        logging.warning("Dry run is enabled. You may find duplicated file names in the output"
                        "as the files are never saved to the target location.")

    _copy_files(source_directory, target_directory, dry_run)


if __name__ == "__main__":
    main()
