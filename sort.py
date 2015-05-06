
'''
Sort a directoy of image files into /year/month/day_hash.* structure.
Non image files are currently ignored. -TODO move to there own folder.

Define input/output directories below. data_in and data_out


Extras: https://pypi.python.org/pypi/ExifRead

'''


def print_tags(tags):
    '''
    Utility function, print out tag keys and values.
    '''
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            print ("Key: {}, value {}".format(tag, tags[tag]))
    print ('---------------- "" ------------------')


def build_structure(structure, root, file):
    '''
    Build directory structure from file meta data, in this case the
    date the photo was taken.
    '''

    file_path = os.path.join(root, file)
    #m_time = os.stat(file_path).st_mtime

    with open(file_path, 'rb') as open_file:
        tags = exifread.process_file(open_file)
        #print_tags(tags)

        try:
            created_at = str(tags['Image DateTime']) # eg. 2013:12:26 15:40:34
        except KeyError:
            print ('No date data found for: {}'.format(file_path))

    # Convert string date into datetime object
    date = datetime.datetime.strptime(created_at, '%Y:%m:%d %H:%M:%S')

    # Build folder structure from date
    year = str(date.year)
    month = '{}. {}'.format(date.strftime('%m'), date.strftime('%B')) # eg. 02. February
    if year in structure:
        if month not in structure[year]:
            structure[year].update({month: [file_path]})
        else:
            structure[year][month].append(file_path)
    else:
        structure[year] = {month: [file_path]}

    return structure


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

            # Get file m time
            file_path = os.path.join(root, f)
            m_time = os.stat(file_path).st_mtime

            # Build folder structure from file m time
            date = datetime.datetime.fromtimestamp(m_time)
            year = str(date.year)

            folder_path = '{}{}/{}. {}'.format(
                data_out,
                year,
                date.strftime('%m'),
                date.strftime('%B'))

            # Create directories
            try:
                os.makedirs(folder_path)
            except FileExistsError:
                pass

            # Create filename
            with open(file_path, 'rb') as open_file:
                file_hash = sha1(open_file.read()).hexdigest()

            _, extension = os.path.splitext(file_path)
            filename = '/{}_{}{}'.format(
                date.strftime('%d'),
                file_hash,
                extension.lower())

            # Copy files to new homes
            #print('copying: ' + folder_path + '/'+ filename)
            copy2(file_path, folder_path + '/'+ filename)

    print(structure)
