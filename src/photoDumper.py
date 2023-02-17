import datetime
import os
import shutil
import sys
from tqdm import tqdm

def get_unique_file_name(source_file_path, modification_date, target_directory, index = 0):
    postfix = ''

    if (index > 0):
        postfix = f'_{index}'

    file_name = f"IMG_{modification_date.strftime('%Y%m%d')}_{modification_date.strftime('%H%M%S')}{postfix}.JPG"
    target_file_path = f'{target_directory}\\{file_name}'

    if (os.path.isfile(target_file_path)):
        # Check if the target file size is equal with the size of the source file
        target_file_size = os.path.getsize(target_file_path)
        source_file_size = os.path.getsize(source_file_path)

        if (target_file_size == source_file_size):
            # File is a duplicate
            return None
        else:
            index += 1
            return get_unique_file_name(source_file_path, modification_date, target_directory, index)
    else:
        return file_name

if (len(sys.argv) != 3):
    sys.exit("Expected arguments: photo_source_directory, photo_target_directory")

photo_source_directory = sys.argv[1]
photo_target_directory = sys.argv[2]

# Validate parameters
if not os.path.isdir(photo_source_directory):
    sys.exit(f"{photo_source_directory} is not a valid directory.")

if not os.path.isdir(photo_target_directory):
    sys.exit(f"{photo_target_directory} is not a valid directory.")

directories = os.walk(photo_source_directory)

for directory in directories:
    # Check if directory should be excluded
    source_folder = directory[0].split('\\')[-1]
    if (source_folder[0] == '.'):
        print(f"{directory[0]}: skipped (hidden folder).")
        continue

    # Get files in directory
    files = directory[2]
    if (len(files) > 0):
        skipped_files = 0
        with tqdm(total=len(files), desc=f"{directory[0]} ({skipped_files} skipped)") as pbar:
            for file in files:
                if (not (file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'))):
                    continue

                source_file_path = f'{directory[0]}\\{file}'
                last_modified = os.path.getmtime(source_file_path)

                modification_date = datetime.datetime.fromtimestamp(last_modified)
                target_folder = modification_date.strftime('%Y\\%m')
                target_folder_path = f'{photo_target_directory}\\{target_folder}'
                target_file_name = get_unique_file_name(source_file_path, modification_date, target_folder_path)
                
                if (target_file_name):
                    target_file_path = f'{target_folder_path}\\{target_file_name}'
                    os.makedirs(target_folder_path, exist_ok=True)
                    shutil.copyfile(source_file_path, target_file_path)
                    # print(f'{source_file_path} copied to {target_file_path}')
                else:
                    skipped_files += 1
                    pbar.set_description(f"{directory[0]} ({skipped_files} skipped)")
                    # print(f'{source_file_path} skipped (already exists)')
                
                pbar.update(1)
                