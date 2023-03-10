import os
import shutil
import sys
import logging
import piexif

from datetime import datetime
from tqdm import tqdm

def get_original_date_taken(photo_file_path):
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

def check_file_uniqueness(source_file_path, target_file_path):
    if (not os.path.isfile(target_file_path)):
        # The file is not a duplicate
        return True

    target_file_size = os.path.getsize(target_file_path)
    source_file_size = os.path.getsize(source_file_path)

    if (target_file_size == source_file_size):
        # The file is a duplicate
        return False
    
    # The file is not a duplicate, but the file with a given name already exists
    return None

if (len(sys.argv) < 3):
    sys.exit("Expected arguments: photo_source_directory, photo_target_directory")

current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(level=logging.DEBUG, filename=f"photo_dumper_{current_timestamp}.log", filemode="w")

photo_source_directory = sys.argv[1]
photo_target_directory = sys.argv[2]
dryRun = False

# Validate parameters
if not os.path.isdir(photo_source_directory):
    sys.exit(f"{photo_source_directory} is not a valid directory.")

if not os.path.isdir(photo_target_directory):
    sys.exit(f"{photo_target_directory} is not a valid directory.")

if (dryRun):
    logging.warning("Dry run is enabled. You may find duplicated file names in the output as the files are never saved to the target location.")

directories = os.walk(photo_source_directory)

for directory in directories:
    # Check if directory should be excluded
    source_folder = directory[0].split("\\")[-1]
    source_folder_path = directory[0]
    if (len(source_folder) > 0 and source_folder[0] == "."):
        logging.info(f"{source_folder_path} skipped (hidden folder).")
        continue

    # Get files in directory
    files = directory[2]
    if (len(files) > 0):
        skipped_files_count = 0
        duplicate_files_count = 0
        unsupported_files_count = 0
        with tqdm(total=len(files), desc=f"{source_folder_path} ({skipped_files_count} skipped)") as pbar:
            for file in files:
                source_file_path = f"{source_folder_path}\\{file}"

                # Skip unsupported files
                if (not (file.lower().endswith(".jpg") or file.lower().endswith(".jpeg"))):
                    logging.info(f"{source_file_path} skipped (unsupported file type)")
                    unsupported_files_count += 1
                    skipped_files_count += 1
                    pbar.set_description(f"{source_folder_path} ({skipped_files_count} skipped)")
                    pbar.update(1)
                else:
                    creation_date = get_original_date_taken(source_file_path)
                    target_folder = creation_date.strftime("%Y\\%m")
                    target_folder_path = f"{photo_target_directory}\\{target_folder}"

                    source_file_size = os.path.getsize(source_file_path)
                    target_file_name = f"IMG_{creation_date.strftime('%Y%m%d')}_{creation_date.strftime('%H%M%S')}_{source_file_size:08d}.JPG"
                    target_file_path = f"{target_folder_path}\\{target_file_name}"
                    is_unique = check_file_uniqueness(source_file_path, target_file_path)

                    if (is_unique is None):
                        # The file is unique, but a different one with the same name exists
                        skipped_files_count += 1
                        pbar.set_description(f"{source_folder_path} ({skipped_files_count} skipped)")
                        pbar.update(1)
                        logging.warning(f"{source_file_path} skipped (a file with this name already exists)")
                    else:
                        if (is_unique):
                            # This is a new file
                            if (not dryRun):
                                if not os.path.exists(target_folder_path):
                                    os.makedirs(target_folder_path, exist_ok=True)
                                shutil.copyfile(source_file_path, target_file_path)
                            logging.info(f"{source_file_path} copied to {target_file_path}")
                        else:
                            # The file is a duplicate
                            skipped_files_count += 1
                            duplicate_files_count += 1
                            pbar.set_description(f"{directory[0]} ({skipped_files_count} skipped)")
                            pbar.update(1)
                            logging.info(f"{source_file_path} skipped (duplicate)")
        
        logging.info(f"""
        Operation summary for {source_folder_path}:
        COPIED: {len(files) - skipped_files_count}
        DUPLICATES: {duplicate_files_count}
        CONFLICTS: {skipped_files_count - duplicate_files_count - unsupported_files_count}
        UNSUPPORTED: {unsupported_files_count}""")
