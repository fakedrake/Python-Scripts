#!/usr/bin/env python

from itertools import izip_longest
from zipfile import ZipFile
import os
import re


def zip_files(file_list, filename):
    with ZipFile(filename, 'w') as f:
        for i in file_list:
            if not i:
                return
            f.write(i)

def group_by(lst, n):
    args = [iter(lst)]*n
    return izip_longest(*args, fillvalue=None)

if __name__ == "__main__":
    files = [i for i in sorted(os.listdir('.')) if re.search(".ppt$", i)]
    for n,i in enumerate(group_by(files, 5)):
        zip_files(i,"packet_%d.zip" % n)
