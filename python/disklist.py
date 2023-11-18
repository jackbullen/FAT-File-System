#! /usr/bin/env python3
import sys
from datetime import datetime
from utils import get_boot_sector, get_fat_info, get_root_directory, get_block

block_size = None

def list_directory_contents(image_file, directory_path):
    pass

def main():
    global block_size 
    
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: disklist <image_file> <directory_path>\n")
        sys.exit(1)

    image_file = sys.argv[1]
    directory_path = sys.argv[2]
    with open(image_file, "rb") as f:
        os_name, block_size, block_count, fat_start, fat_blocks, root_dir_start, root_dir_blocks = get_boot_sector(f)
        root = get_root_directory(f, block_size, root_dir_start, root_dir_blocks)
        fat = get_fat_info(f, fat_start, fat_blocks, block_size, root)

        ####        TODO

        ####   1. Add logic to find the requested directory_path
        ####   2. List that directory instead of the root

        for entry in root.values():
            # print("Directory entry:", entry['filename'], entry['status'])
            # print("Starting block:", entry['start_block'])
            # print(f'{entry["num_blocks"]} total blocks')

            # file in the directory
            if entry['status'] == 3:
                file_type = "F"

            # subdirectory
            elif entry['status'] == 5:
                file_type = "D"

            # neither file nor directory
            else:
                continue

            file_size = f"{entry['file_size']:>10}"
            file_name = entry['filename'].strip('\x00')
            file_name = f"{file_name:>30}"
            creation_time = entry['creation_time']

            print(f"{file_type} {file_size} {file_name} {creation_time}")

            if entry["num_blocks"] > 1:
                a = get_block(f, entry['start_block'], block_size)
                f.seek(fat_start*block_size + entry['start_block']*4, 0)
                curr = int.from_bytes(f.read(4), 'big')
                a += get_block(f, curr, block_size)
                while curr != 0xffffffff:
                    curr = fat[curr]
                    a += get_block(f, curr, block_size)

if __name__ == "__main__":
    main()