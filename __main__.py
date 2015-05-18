
import os

import image_sort


if __name__ == "__main__":

    data_in = 'C:/Users/Sam/Documents/data_in/'
    data_out = 'C:/Users/Sam/Documents/data_out/'
    data_unsorted = '{}unsorted/'.format(data_out)

    image_sort.setup(data_out, data_unsorted)
    structure = {}
    for root, sub_dirs, files in os.walk(data_in):
        for f in files:
            structure = image_sort.build_structure(structure, root, f, data_unsorted)
    image_sort.print_structure(structure)
    image_sort.output(structure, data_out)
