import os.path

from os import listdir, replace
from os.path import isfile, join

def remove_small_files(files, path, size=52_430_000):
    filenames_to_move = []
    unused_files_path = os.path.join(path, "unused")
    if not os.path.exists(unused_files_path):
        os.makedirs(unused_files_path)

    for file in files:
        abspath = os.path.join(path, file)
        if os.path.getsize(abspath) < size:
            os.rename(abspath, os.path.join(unused_files_path, file))


def save_parameters():
    while True:
        try: path = input("Location: "); break
        except e: print(f"\tError: {e}")

    while True:
        size_mb = input("Maximum size in MB (def. 50 MB): ")
        if size_mb.strip() == "" or size_mb.strip() == " ":
            size_mb = 50
            break
        try:
            size_mb = float(size_mb)
            break
        except ValueError as e:
            print(f"\tError: {e}")

    size = int(size_mb * 1_048_576)
    return path, size

def main():
    path, size = save_parameters()
    files = [f for f in listdir(path) if isfile(join(path, f))]
    remove_small_files(files, path, size)

if __name__ == "__main__":
    main()
