
"""
Sort a directoy of image files into /year/month/day_hash.* structure.
Non image files, and images without meta data are moved to directory for manual
sorting.

Requirments:
    https://pypi.python.org/pypi/ExifRead

"""

import datetime
import exifread
import os
import sys

from hashlib import sha1
from shutil import copy2


def create_filename(file_path, date=None):
    """
    Create unique filename using day of month and hash of file content
    """
    with open(file_path, 'rb') as open_file:
        file_hash = sha1(open_file.read()).hexdigest()

    _, extension = os.path.splitext(file_path)
    filename = '{}{}'.format(
            file_hash,
            extension.lower())

    if date:
        day = '{}'.format(date.strftime('%d'))
        filename = '{}_{}'.format(day, filename)

    return filename


def build_structure(structure, root, file, data_unsorted):
    """
    Build directory structure from file meta data, in this case the
    date the photo was taken, if no meta data found copy file into unsorted
    directory for manual sorting later.
    """
    file_path = os.path.join(root, file)
    with open(file_path, 'rb') as open_file:
        tags = exifread.process_file(open_file)
        try:
            created_at = str(tags['Image DateTime']) # eg. 2013:12:26 15:40:34
        except KeyError:
            print ('No date data found for: {}'.format(file_path))
            unsorted(file_path, data_unsorted, create_filename(file_path))
            return structure

    # Convert string date into datetime object
    date = datetime.datetime.strptime(created_at, '%Y:%m:%d %H:%M:%S')
    new_filename = create_filename(file_path, date)

    # Build structure for directories and files from date
    year = str(date.year)
    month = '{}. {}'.format(date.strftime('%m'), date.strftime('%B')) # eg. 02. February
    if year in structure:
        if month not in structure[year]:
            structure[year].update({month: [(file_path, new_filename)]})
        else:
            structure[year][month].append((file_path, new_filename))
    else:
        structure[year] = {month: [(file_path, new_filename)]}
    return structure


def output(structure, data_out):
    """
    Create directories and copy files as outlined in structure.
    """
    # Create directories
    directories = 0
    files = 0
    for year in structure.keys():
        for month in structure[year].keys():
            directory = '{}{}/{}/'.format(
                data_out,
                year,
                month)
            try:
                os.makedirs(directory)
                directories += 1
            except FileExistsError:
                pass

            # Copy files into new directories
            for original, filename in structure[year][month]:
                if not os.path.exists(directory + filename):
                    copy2(original, directory + filename)
                    files += 1
    print ('Copy complete: {} directories and {} files created.'.format(
        directories, files))


def print_tags(tags):
    """
    Utility function, print out image tag keys and values.
    """
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            print ("Key: {}, value {}".format(tag, tags[tag]))
    print ('---------------- "" ------------------')


def print_structure(structure):
    """
    Utility function, format printing of new directory/file structure.
    """
    print ('---------------- "" ------------------')
    print ('New Structure:')
    print ('----------------')
    for year in structure.keys():
        for month in structure[year].keys():
            print ('{}/{}/'.format(year, month))
            for original, filename in structure[year][month]:
                print ('  {}'.format(filename))
    print ('---------------- "" ------------------')


def setup(data_out, data_unsorted):
    """
    Ensure check output directories exist.
    """

    if not os.path.isdir(data_out):
        try:
            os.makedirs(data_out)
        except FileExistsError:
            pass

    if not os.path.isdir(data_unsorted):
        try:
            os.makedirs(data_unsorted)
        except FileExistsError:
            pass


def unsorted(file_path, directory, filename):
    if not os.path.exists(directory + filename):
        copy2(file_path, directory + filename)

