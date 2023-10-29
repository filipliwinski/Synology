# Copyright (c) Filip Liwiński
# Licensed under the MIT License. See the LICENSE file in the project root for license information.

"""Allows to copy photos from a local directory to Synology Photos."""
import os
import shutil
import sys
import logging
import hashlib
from datetime import datetime
import piexif

from tqdm import tqdm
from version import __version__
from file_stats import FileStats

EXIF_DATE_TIME_ORGINAL = "0x9003"
TARGET_FILE_NAME_PREFIX = "IMG"
TARGET_FILE_FORMAT = "JPG"

def _get_original_date_taken(photo_file_path):
    """
    Retrieves the creation date of the photo from the EXIF metadata. 
    If the EXIF data is not present returns the last modified date.
    """

    # Load the EXIF data from the file
    exif_data = piexif.load(photo_file_path)

    # Get the value of the DateTimeOriginal tag (0x9003) from the EXIF data
    date_taken = exif_data["Exif"].get(EXIF_DATE_TIME_ORGINAL)

    # If the tag is present, convert the value to a datetime object and return it
    if date_taken:
        date_taken_str = date_taken.decode("utf-8")
        return datetime.strptime(date_taken_str, "%Y:%m:%d %H:%M:%S")

    # If the tag is not present or is invalid, return last modified date
    last_modified = os.path.getmtime(photo_file_path)
    return datetime.fromtimestamp(last_modified)

def _calculate_file_hash(file_path):
    """
    Calculates the hash of the provided file using the SHA-256 alghoritm.
    """

    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as file:
            file_bytes = file.read()
            sha256.update(file_bytes)

        file_hash = sha256.hexdigest()

        return file_hash
    except OSError:
        logging.exception("Unable to calculate hash of file %s", file_path)

    return ""

def _check_file_uniqueness(file_path, destination_file_path):
    """
    Returns True if the file is not a duplicate and a file with a given name
    does not exist in the target location. If the file is a duplicate, returns False
    and if a file with the given name already exists, returns None.

    Uses file hash to determine uniqueness.
    """

    if not os.path.isfile(destination_file_path):
        # The file is not a duplicate
        return True

    destination_file_hash =  _calculate_file_hash(destination_file_path)
    file_hash = _calculate_file_hash(file_path)

    if destination_file_hash == file_hash:
        # The file is a duplicate
        return False

    # The file is not a duplicate, but a file with a given name already exists
    return None


def _verify_and_copy_file(file, source_file_path, target_directory, dry_run, file_stats):
    """
    Verifies and copies the given file from the provided source directory to the target directory.
    """

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
            f"{TARGET_FILE_NAME_PREFIX}_"
            f"{creation_date.strftime('%Y%m%d')}_"
            f"{creation_date.strftime('%H%M%S')}_"
            f"{source_file_size:08d}.{TARGET_FILE_FORMAT}")
        target_file_path = f"{target_folder_path}\\{target_file_name}"
        is_unique = _check_file_uniqueness(
            source_file_path, target_file_path)

        if is_unique is None:
            # The file is unique, but a different one with the same name exists
            file_stats.report_conflict()
            logging.warning(
                "%s skipped (conflict - a file with the given name already exists)",
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
                file_stats.report_copied()
                logging.info("%s copied to %s",
                                source_file_path, target_file_path)

            else:
                # The file is a duplicate
                file_stats.report_duplicate()
                logging.info(
                    "%s skipped (duplicate)", source_file_path)

def _verify_and_copy_files(source_directory, target_directory, dry_run):
    """Verifies and copies files from the provided source directory to the target directory."""

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
            file_stats = FileStats()
            with tqdm(total=len(files),
                      desc=f"{source_folder_path} ({file_stats.skipped} skipped)") as pbar:
                for file in files:
                    source_file_path = f"{source_folder_path}\\{file}"

                    _verify_and_copy_file(
                        file, source_file_path, target_directory, dry_run, file_stats)

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

    script_name = f"Photo Dumper v.{__version__}"
    logging.info(script_name)
    print(script_name)

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

    _verify_and_copy_files(source_directory, target_directory, dry_run)


if __name__ == "__main__":
    main()
