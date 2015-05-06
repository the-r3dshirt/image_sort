
'''
Sort a directoy of image files into /year/month/day_hash.* structure.
Non image files are currently ignored. -TODO move to there own folder.

Define input/output directories below. data_in and data_out


Extras: https://pypi.python.org/pypi/ExifRead

'''


def create_filename(file_path, date):
    '''
    Create unique filename using day of month and hash of file content
    '''
    with open(file_path, 'rb') as open_file:
        file_hash = sha1(open_file.read()).hexdigest()

    _, extension = os.path.splitext(file_path)
    filename = '{}_{}{}'.format(
        date.strftime('%d'),
        file_hash,
        extension.lower())
    return filename


def build_structure(structure, root, file):
    '''
    Build directory structure from file meta data, in this case the
    date the photo was taken.
    '''
    file_path = os.path.join(root, file)
    with open(file_path, 'rb') as open_file:
        tags = exifread.process_file(open_file)
        #print_tags(tags)

        try:
            created_at = str(tags['Image DateTime']) # eg. 2013:12:26 15:40:34
        except KeyError:
            print ('No date data found for: {}'.format(file_path))
            # Default to using mtime?
            #m_time = os.stat(file_path).st_mtime
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


def print_tags(tags):
    '''
    Utility function, print out tag keys and values.
    '''
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            print ("Key: {}, value {}".format(tag, tags[tag]))
    print ('---------------- "" ------------------')


if __name__ == "__main__":
    import datetime
    import exifread
    import os
    import sys

    from hashlib import sha1
    from shutil import copy2

    data_in = './data_in/'
    data_out = './data_out/'

    structure = {}
    for root, sub_dirs, files in os.walk(data_in):
        for f in files:
            structure = build_structure(structure, root, f)

    print(structure)

    # Create directories
    for year in structure.keys():
        for month in structure[year].keys():
            directory = '{}{}/{}/'.format(
                data_out,
                year,
                month)
            try:
                os.makedirs(directory)
            except FileExistsError:
                pass

            # Copy files into new directories
            data = structure[year][month]
            for original, filename in data:
                print('{}: {}{}'.format(original, directory, filename))
                copy2(original, directory + filename)
