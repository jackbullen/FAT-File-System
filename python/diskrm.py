#! /usr/bin/env python3
import sys
from utils import (get_boot_sector, get_fat_info, get_file_system,
                   write_file_to_disk, update_fat, update_directory,
                   get_directory)

def main():
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: diskput <image_file> <file_to_remove>\n")
        sys.exit(1)

    image_file = sys.argv[1]
    file_to_remove = sys.argv[2]

    try:
        with open(image_file, "r+b") as f:
            os_name, block_size, block_count, fat_start, fat_blocks, root_dir_start, root_dir_blocks = get_boot_sector(f)
            fat = get_fat_info(f, fat_start, fat_blocks, block_size)
            file_system = get_file_system(f, root_dir_blocks, block_size, fat, root_dir_start)

            file_name = file_to_remove.split('/')[-1]

            dir = '/'.join(file_to_remove.split('/')[:-1])
            if dir == '':
                dir = '/'

            try:
                entry = [x for x in file_system[dir]['entries'] if x['file_name'] == file_name][0]
            except IndexError:
                sys.stderr.write("File not found.\n")
                sys.exit(1)

            # 1. Clear the data blocks
            curr = entry['start_block']
            for _ in range(entry['num_blocks']):
                f.seek(curr * block_size, 0)
                # print(f.read(block_size))
                f.write(bytes([0x00] * block_size))
                curr = fat[curr]

            # 2. Clear the FAT entries
            f.seek(fat_start * block_size, 0)
            for _ in range(entry['start_block']):
                f.read(4)
            for _ in range(entry['num_blocks']):
                # print(int.from_bytes(f.read(4), 'big'))
                f.write(bytes([0x00] * 4))
            
            # 3. Clear the directory entry
            if dir == '/':
                dir_entry = {'num_blocks': root_dir_blocks, 'start_block': root_dir_start}
            else:
                dir_entry = [x for x in file_system['/'.join(dir.split('/')[:-1])]['entries'] if x['file_name'] == dir.split('/')[-1]][0]

            f.seek(dir_entry['start_block'] * block_size, 0)
            for _ in range(dir_entry['num_blocks']):
                status = int.from_bytes(f.read(1), 'big')
                starting_block = int.from_bytes(f.read(4), 'big')
                num_blocks = int.from_bytes(f.read(4), 'big')
                file_size = int.from_bytes(f.read(4), 'big')
                year = int.from_bytes(f.read(2), 'big')
                month = int.from_bytes(f.read(1), 'big')
                day = int.from_bytes(f.read(1), 'big')
                hour = int.from_bytes(f.read(1), 'big')
                minute = int.from_bytes(f.read(1), 'big')
                second = int.from_bytes(f.read(1), 'big')
                creation_time = f"{year:04d}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
                modification_time = int.from_bytes(f.read(7), 'big')
                filename = f.read(31).decode("utf-8").strip('\x00')
                filler = f.read(6)
                # if file to be removed equals the file we just read in from the dir entry,
                # go back 64 bytes and set the status byte to 0x00
                if file_name == filename:
                    f.seek(-64, 1)
                    # print(int.from_bytes(f.read(1), 'big'))
                    f.write(bytes([0x00]))
                    break

            # 4. Update superblock...
            
    except FileNotFoundError:
        sys.stderr.write("Error: File or image not found.\n")
        sys.exit(1)
    # except Exception as e:
    #     sys.stderr.write(f"Error: {e}\n")
    #     sys.exit(1)

if __name__ == "__main__":
    main()
