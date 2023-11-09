#! /usr/bin/env python3
import sys
import os

BOOT_SECTOR_SIZE = 512

def get_fat_info(f, fat_start, fat_blocks, block_size, root):
    '''
        Returns file allocation table
    '''
    file_access_table = dict()
    print("FAT Information")
    free_blocks = 0
    reserved_blocks = 0
    allocated_blocks = 0
    f.seek(fat_start * block_size, 0)
    print(fat_start*block_size)

    mapped_blocks = 0
    for i , file in root.items():
        print(i,file['num_blocks'])
        mapped_blocks += file['num_blocks']
    print(fat_blocks*block_size//4)
    for i in range(fat_blocks*block_size//4):
        fat_entry = f.read(4)
        
        entry_value = int.from_bytes(fat_entry, 'big')
        file_access_table[i] = entry_value
        if entry_value == 0x00:
            free_blocks +=1
        elif entry_value == 0x01:
            reserved_blocks += 1
        else:
            allocated_blocks += 1

    
    # for i, file in root.items():
    #     if file['num_blocks'] > 1:
    #         for j in range(1, file['num_blocks']):
    #             file_access_table[file['start_block'] + j] = 0x02

    print("Free Blocks: {}".format(free_blocks))
    print("Reserved Blocks: {}".format(reserved_blocks))
    print("Allocated Blocks: {}".format(allocated_blocks))
    return file_access_table

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: diskinfo <image_file>\n")
        sys.exit(1)

    filename = sys.argv[1]

    with open(filename, "rb") as f:
        boot_sector = f.read(BOOT_SECTOR_SIZE)

        block_size = int.from_bytes(boot_sector[8:10], 'big')
        block_count = int.from_bytes(boot_sector[10:14],'big')
        
        fat_start = int.from_bytes(boot_sector[14:18],'big')
        fat_blocks = int.from_bytes(boot_sector[18:22],'big')

        root_dir_start = int.from_bytes(boot_sector[22:26],'big')
        root_dir_blocks = int.from_bytes(boot_sector[26:30],'big')

        os_name = boot_sector[0:8].decode("utf-8")
        print(os_name)
        print("==============")
        print("Super block information")
        print("Block size:", block_size)
        print("Block count:", block_count)
        print("Fat starts:", fat_start)
        print("FAT blocks:", fat_blocks)
        print("Root directory start:", root_dir_start)
        print("Root directory blocks:", root_dir_blocks)

        print("==============")

        # GETTING ROOT DIR
        print("ROOT DIR")

        f.seek(root_dir_start * block_size, 0)
        root = dict()
        for i in range(root_dir_blocks):
            status = int.from_bytes(f.read(1), 'big')
            starting_block = int.from_bytes(f.read(4), 'big')
            num_blocks = int.from_bytes(f.read(4), 'big')
            file_size = int.from_bytes(f.read(4), 'big')
            creation_time = int.from_bytes(f.read(7), 'big')
            modification_time = int.from_bytes(f.read(7), 'big')
            filename = f.read(31).decode("utf-8")
            print(filename)
            filler = f.read(6)
            root[i] = {
                'status':status, 
                'filename': filename, 
                'start_block': starting_block, 
                'num_blocks': num_blocks, 
                'file_size': file_size, 
                'creation_time': creation_time, 
                'modification_time': modification_time
            }
            # print(f.read(root_dir_blocks * block_size))
            # print('status:',status)
            # print('starting_block:',starting_block)
            # print('num_blocks:',num_blocks)
            # print('file_size:',file_size)
            # print('creation_time:',creation_time)
            # print('modification_time:',modification_time)
            # print('filename:',filename)
            # print('filler:',filler)
            # print("==============")
        # GETTING FAT

        fat = get_fat_info(f, fat_start, fat_blocks, block_size, root)
        
        # print(fat.items())
        data = dict()
        print(root.items())
        for i, file in root.items():
            f.seek(file['start_block'] * block_size, 0)
            data[i] = f.read(file['start_block'] * block_size)
            print(i, file['start_block'], file['num_blocks'], fat[i+1], file['filename'])
            if file['num_blocks'] > 1:
                
                for j in range(1, file['num_blocks']):
                    f.seek(fat[i+j]*block_size, 0)
                    data[i] += f.read(block_size)
        print(fat.items())
        for i, entry in root.items():
            lookup_fat(fat, i, entry)

            print("Root directory entry:", i, entry['filename'])
            print("Starting block:", entry['start_block'])
            print(f'{entry["num_blocks"]} total blocks')

            if entry["num_blocks"] > 1:
                
                print('looking up in fat:', (entry['start_block']))
                a = get_block(f, entry['start_block'], block_size)
                f.seek(fat_start*block_size + entry['start_block']*4, 0)
                curr = int.from_bytes(f.read(4), 'big')
                a += get_block(f, curr, block_size)
                while curr != 0xffffffff:
                    print(curr)
                    curr = fat[curr]
                    print(curr)
                    a += get_block(f, curr, block_size)
                print(a)
                print("+"*14 + '\n')
            # for i in range(file['num_blocks']):
            #     fat_entry = f.read(4)
            #     print(fat_entry)
            #     entry_value = int.from_bytes(fat_entry, 'big')
            # print("+"*14 + '\n')
                # print(entry_value)

def lookup_fat(fat, i, entry):
    lookup = fat[i]
    # if entry['start_block'] > 1:
        # print(i, entry, lookup)
        # if lookup>1:
            # print("NEED TO LOOKUP")

def get_block(f, block_number, block_size):
    f.seek(block_number * block_size)
    return f.read(block_size)

if __name__ == "__main__":
    main()