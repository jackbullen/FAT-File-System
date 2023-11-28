#! /usr/bin/env python3
import sys
from utils import (get_boot_sector, get_fat_info, get_file_system,
                   write_file_to_disk, update_fat, update_directory)

def main():
    if len(sys.argv) != 4:
        sys.stderr.write("Usage: diskput <image_file> <source_path> <destination_path>\n")
        sys.exit(1)

    image_file = sys.argv[1]
    source_path = sys.argv[2]
    destination_path = sys.argv[3]

    try:
        with open(image_file, "r+b") as f, open(source_path, "rb") as source_file:
            os_name, block_size, block_count, fat_start, fat_blocks, root_dir_start, root_dir_blocks = get_boot_sector(f)
            fat = get_fat_info(f, fat_start, fat_blocks, block_size)
            file_data = source_file.read()
            file_system = get_file_system(f, root_dir_blocks, block_size, fat, root_dir_start)

            # 1. Write the file into the blocks
            start_block = write_file_to_disk(f, file_data, fat, block_size, root_dir_start, root_dir_blocks)
            
            # 2. Update the FAT
            update_fat(f, fat, fat_start, block_size) 

            # 3. Update the directory
            update_directory(f, destination_path, file_data, start_block, block_size, file_system, root_dir_start, root_dir_blocks) 

    except FileNotFoundError:
        sys.stderr.write("Error: File or image not found.\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()