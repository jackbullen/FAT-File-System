#! /usr/bin/env python3
import sys
from utils import get_boot_sector, get_fat_info, get_file_system, print_entries

def main():
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: disklist <image_file> <directory_path>\n")
        sys.exit(1)

    image_file = sys.argv[1]
    directory_path = sys.argv[2]

    with open(image_file, "rb") as f:
        # Get super block, root, and fat
        os_name, block_size, block_count, fat_start, fat_blocks, root_dir_start, root_dir_blocks = get_boot_sector(f)
        fat = get_fat_info(f, fat_start, fat_blocks, block_size)

        # Get the file system and print the entries for requested directory_path
        file_system = get_file_system(f, root_dir_blocks, block_size, fat, root_dir_start)
    
        try:
            entries = file_system[directory_path]['entries']
            print_entries(entries)
        except KeyError:
            sys.stderr.write("Directory not found\n")

if __name__ == "__main__":
    main()