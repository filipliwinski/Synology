# Synology

[![Pylint](https://github.com/filipliwinski/Synology/actions/workflows/pylint.yml/badge.svg)](https://github.com/filipliwinski/Synology/actions/workflows/pylint.yml)

This repository contains a set of Python scripts that streamline processes not supported by Synology services (e.g. Synology Photos). Each script is responsible for its own purpose and is documented in a README file located in the script's directory.

## How to contribute?

If you have a problem with your Synology NAS that can be solved programatically, but you don't know exactly how to do it or you have an idea about a new script that can be part of this repository - please create an issue.

Everyone is welcome to contribute by creating forks and making Pull Requests to this repository with their own scripts and tools.

## Avaliable scripts

The full list of the scripts can be found below.

### Photo Dumper

This Python script allows you to import photos to your Synology NAS form a local disk, an external drive, a removable storage (such as a USB stick and SD cards) or even from the NAS itself. The script organises photos in folders in the target directory in the same way Synology Photos does, based on the dates the photos were taken.

[Read full description.](https://github.com/filipliwinski/Synology/tree/master/src/photo_dumper)

## Planned scripts

Below are listed ideas of scripts that may be developed in the future. There is no ETA and priority specified. Feel free to create an issue to discuss about any of them.

### Photo Cleaner

Synology Photos shows photos stored in hidden folders (unix style). This script will allow to remove files stored in hidden folders, that are created by third party tools (like Google Picasa, which stores originals of  edited photos in folders called _.picasaoriginals_). It will alow to specify number of hours/days after which these original photos will be removed.

### Photo Slideshow

It is possible to display a slideshow directly in the Synology Photos web interface, but it is very limited (it can be only run for one Album/tag, the speed of the slideshow cannot be adjused, nor the order of the photos). The script will allow to select multiple tags, specifiy start and end dates and will cache the images on the device if needed.
