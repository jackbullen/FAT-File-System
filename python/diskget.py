#! /usr/bin/env python3
import sys
from utils import get_boot_sector, get_fat_info, get_file_system

def main():
    if len(sys.argv) != 4:
        sys.stderr.write("Usage: diskget <image_file> <file_path> <destination_path>\n")
        sys.exit(1)
    
    image_file = sys.argv[1]
    file_path = sys.argv[2]
    destination_path = sys.argv[3]

    with open(image_file, "rb") as f:
        # Get super block, root, and fat
        os_name, block_size, block_count, fat_start, fat_blocks, root_dir_start, root_dir_blocks = get_boot_sector(f)
        fat = get_fat_info(f, fat_start, fat_blocks, block_size)

        file_system = get_file_system(root_dir_blocks, block_size, fat, root_dir_start)

        path = file_path.split('/')[:-1]
        dir = '/'.join(path)

        file_name = file_path.split('/')[-1]

        with open(destination_path, 'wb') as destination:
            destination.write(file_system[dir]['files'][file_name])

if __name__ == "__main__":
    main()