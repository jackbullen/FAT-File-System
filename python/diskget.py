#! /usr/bin/env python3
import sys
from utils import get_boot_sector, get_root_directory, get_block, get_fat_info, BOOT_SECTOR_SIZE

block_size = None

def get_subdir(f, fat, root, ent):
    pass

def locate_file(f, fat, root, file_path):
    file_directory = root
    for ent in file_path.split('/')[1:]:
        if len(ent.split('.')) > 1:
            # at the file
            file = [file for file in file_directory.values() if file['filename'].strip('\x00')==ent][0]
            return file['start_block'], file['num_blocks']
        else:
            ####     TODO

            ####  1. Implement get_subdir to return the subdirs so we can find the file if it's not in the root.
            file_directory = get_subdir(f, fat, root, ent)

    # directories = [entry for entry in root.values() if entry['status']==1]
    # files = [entry for entry in root.values() if entry['status']==3]
    # print(files,directories)
    return 0,0

def get_file_from_image(f, fat, root, file_path, destination_path):
    global block_size
    starting_block, num_blocks = locate_file(f, fat, root, file_path)
    curr = starting_block

    with open(destination_path, 'wb') as dest_file:
        for _ in range(num_blocks):
            block_data = get_block(f, curr, block_size)
            dest_file.write(block_data)
            curr = fat[curr]

def main():
    global block_size

    if len(sys.argv) != 4:
        sys.stderr.write("Usage: diskget <image_file> <file_path> <destination_path>\n")
        sys.exit(1)
    
    image_file = sys.argv[1]
    file_path = sys.argv[2]
    destination_path = sys.argv[3]

    with open(image_file, "rb") as f:
        os_name, block_size, block_count, fat_start, fat_blocks, root_dir_start, root_dir_blocks = get_boot_sector(f)
        root = get_root_directory(f, block_size, root_dir_start, root_dir_blocks)
        fat = get_fat_info(f, fat_start, fat_blocks, block_size, root)
        get_file_from_image(f, fat, root, file_path, destination_path)

if __name__ == "__main__":
    main()