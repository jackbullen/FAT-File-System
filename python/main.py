#! /usr/bin/env python3
import sys
import os

BOOT_SECTOR_SIZE = 512

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: diskinfo <image_file>\n")
        sys.exit(1)

    filename = sys.argv[1]

    with open(filename, "rb") as f:
        boot_sector = f.read(BOOT_SECTOR_SIZE)

        block_size = int.from_bytes(boot_sector[8:10])
        block_count = int.from_bytes(boot_sector[10:14])

        fat_start = int.from_bytes(boot_sector[14:18])
        fat_blocks = int.from_bytes(boot_sector[18:22])

        block_root_dir_start = int.from_bytes(boot_sector[22:26])
        block_root_dir_blocks = int.from_bytes(boot_sector[26:30])

        root_dir_start = fat_start + fat_blocks
        root_dir_blocks = block_count // block_size

        os_name = boot_sector[0:7].decode("utf-8")

        print("OS Name: {}".format(os_name))
        print("Label of the disk: {}".format(filename))
        print("Total size of the disk: {} bytes".format(block_count * block_size))
        print("Free size of the disk: {} bytes".format(0))
        print("==============")
        print("The number of FAT copies: {}".format(2))
        print("Sectors per FAT: {}".format(fat_blocks))
        print("==============")
        print("Root Directory Start: {}".format(root_dir_start))
        print("Root Directory Blocks: {}".format(root_dir_blocks))
        print("==============")
        print("Block size: {}".format(block_size))
        print("Block count: {}".format(block_count))
        print("==============")
        print("FAT starts: {}".format(fat_start))
        print("FAT blocks: {}".format(fat_blocks))
        print("==============")
        print("Block of root directory starts: {}".format(block_root_dir_start))
        print("Block of root directory blocks: {}".format(block_root_dir_blocks))
        print("==============")

        free_blocks = 0
        reserved_blocks = 0
        allocated_blocks = 0

        f.seek(fat_start * block_size)

        for i in range(block_count):
            fat_entry = f.read(2)
            entry_value = int.from_bytes(fat_entry)

            if entry_value == 0x00:
                free_blocks +=1
            elif 0xFF00 <= entry_value <= 0xFFFF:
                reserved_blocks += 1
            else:
                allocated_blocks += 1
                start_pos = i * block_size
                f.seek(start_pos)
                block_content = f.read(block_size)
                try:
                    content = block_content.decode("utf-8")
                    print(f"Block {i}\n", content)
                except UnicodeDecodeError:
                    print(f"Block {i} contains invalid UTf-8 data")
                
        print("Free Blocks: {}".format(free_blocks))
        print("Reserved Blocks: {}".format(reserved_blocks))
        print("Allocated Blocks: {}".format(allocated_blocks))

if __name__ == "__main__":
    main()