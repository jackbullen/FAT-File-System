#! /usr/bin/env python3
import sys
from utils import get_boot_sector, get_fat_info

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: diskinfo <image_file>\n")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, "rb") as f:
        os_name, block_size, block_count, fat_start, fat_blocks, root_dir_start, root_dir_blocks = get_boot_sector(f)

        # print(os_name)
        # print("==============")
        print("Super block information")
        print("Block size:", block_size)
        print("Block count:", block_count)
        print("Fat starts:", fat_start)
        print("FAT blocks:", fat_blocks)
        print("Root directory start:", root_dir_start)
        print("Root directory blocks:", root_dir_blocks)
        print()
        # print("==============")
        get_fat_info(f, fat_start, fat_blocks, block_size, verbose=True)

if __name__ == "__main__":
    main()