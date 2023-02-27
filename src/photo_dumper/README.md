# Photo Dumper

This Python script allows you to import photos to your Synology NAS form a local disk, an external drive, a removable storage (such as a USB stick and SD cards) or even from the NAS itself. The script organises photos in folders in the target directory in the same way Synology Photos does, based on the dates the photos were taken.

## Description

[Synology Photos](https://www.synology.com/en-uk/dsm/feature/photos) is a free service available on Synology DSM 7+ which allows to store photos and videos on a local NAS. It comes with a very nice web and mobile clients which are great for viewing and sharing photos, but not so great if you want to move a lot of photos to your NAS at once, while preserving the division of directories by year and month.

This script checks for `.jpg` and `.jpeg` files in the specified source directory, reads the original date taken from the EXIF data of the photos and saves them in the target directory in folders based on the year and month they were taken. It handles duplicated files and verifies the files for corruption after they have been transferred. The srript renames the transferred files to include the date and time the photo was taken and the file size in bytes, e.g. `IMG_20230216_211349_03771730.JPG`, where `20230216` is the date in format `yyyyMMdd`, `211349` is the time in format `hhmmss` and  `03771730` is the size of the file in bytes.
