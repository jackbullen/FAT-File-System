import time

BOOT_SECTOR_SIZE = 512

def get_boot_sector(f):
    boot_sector = f.read(BOOT_SECTOR_SIZE)

    block_size = int.from_bytes(boot_sector[8:10], 'big')
    block_count = int.from_bytes(boot_sector[10:14],'big')
    
    fat_start = int.from_bytes(boot_sector[14:18],'big')
    fat_blocks = int.from_bytes(boot_sector[18:22],'big')

    root_dir_start = int.from_bytes(boot_sector[22:26],'big')
    root_dir_blocks = int.from_bytes(boot_sector[26:30],'big')

    os_name = boot_sector[0:8].decode("utf-8")

    return os_name, block_size, block_count, fat_start, fat_blocks, root_dir_start, root_dir_blocks

def get_fat_info(f, fat_start, fat_blocks, block_size, verbose=False) -> dict:
    '''
        Return file allocation table
    '''
    file_access_table = dict()
    
    free_blocks = 0
    reserved_blocks = 0
    allocated_blocks = 0

    # go to fat start and read until the end
    f.seek(fat_start * block_size, 0)
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

    if verbose:
        print("FAT Information")
        print(f"Free Blocks: {free_blocks}")
        print(f"Reserved Blocks: {reserved_blocks}")
        print(f"Allocated Blocks: {allocated_blocks}")
    return file_access_table

def get_root_directory(f, block_size, root_dir_start, root_dir_blocks) -> dict:
    '''
        Return root directory
    '''
    root = dict()

    # go to start of root and read until the end.
    f.seek(root_dir_start * block_size, 0)
    for i in range(root_dir_blocks*block_size // 64):
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
        filename = f.read(31).decode("utf-8")
        filler = f.read(6)

        # skip the No File entries
        if status == 0:
            continue

        root[i] = {
            'status':status, 
            'filename': filename.strip('\x00'), 
            'start_block': starting_block, 
            'num_blocks': num_blocks, 
            'file_size': file_size, 
            'creation_time': creation_time, 
            'modification_time': modification_time
        }
    return root

def get_block(f, block_number, block_size):
    f.seek(block_number * block_size)
    return f.read(block_size)

def get_directory(dir_bytes, block_size, root_dir_blocks) -> dict:
    '''
        Return root directory
    '''
    entries = list()
    for _ in range(root_dir_blocks*block_size // 64):
            status = int.from_bytes(dir_bytes[0:1], 'big')
            starting_block = int.from_bytes(dir_bytes[1:5], 'big')
            num_blocks = int.from_bytes(dir_bytes[5:9], 'big')
            file_size = int.from_bytes(dir_bytes[9:13], 'big')
            year = int.from_bytes(dir_bytes[13:15], 'big')
            month = int.from_bytes(dir_bytes[15:16], 'big')
            day = int.from_bytes(dir_bytes[16:17], 'big')
            hour = int.from_bytes(dir_bytes[17:18], 'big')
            minute = int.from_bytes(dir_bytes[18:19], 'big')
            second = int.from_bytes(dir_bytes[19:20], 'big')
            creation_time = f"{year:04d}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
            modification_time = int.from_bytes(dir_bytes[20:27], 'big')
            file_name = dir_bytes[27:58].decode("utf-8")
            filler = dir_bytes[58:64]
            dir_bytes = dir_bytes[64:]

            if status == 0:
                continue

            entries.append({
                'status':status, 
                'file_name': file_name.strip('\x00'), 
                'start_block': starting_block, 
                'num_blocks': num_blocks, 
                'file_size': file_size, 
                'creation_time': creation_time, 
                'modification_time': modification_time
            })
    return entries

def get_linked_blocks(f, num_blocks, block_size, dir_start, fat) -> bytes:
    '''
        Return the linked blocks of a file or directory.
    '''
    curr = dir_start
    file = b''
    for _ in range(num_blocks):
        block_data = get_block(f, curr, block_size)
        file += block_data
        curr = fat[curr]
    return file

def get_subdirs(f, file_system, subdirs, parent, block_size, fat, root_dir_blocks):
    '''
        Return a list of subdirectories
    '''
    
    for subdir in subdirs:
        subdir_blocks = get_linked_blocks(f, subdir['num_blocks'], block_size, subdir['start_block'], fat)
        subdir_entries = get_directory(subdir_blocks, block_size, root_dir_blocks)
        file_entries = [file for file in subdir_entries if file['status'] == 3]
        subdir_subdirs = [dir for dir in subdir_entries if dir['status'] == 5]
        files = {}
        for file in file_entries:
            files[file['file_name']] = get_linked_blocks(f, file   ['num_blocks'], block_size, file['start_block'], fat)

        file_system[parent+subdir['file_name']] = {
                                'entries': subdir_entries,
                                'files': files
                            }

        if subdir_entries:
            file_system = get_subdirs(f, file_system, subdir_subdirs, parent+subdir['file_name']+'/', block_size, fat, root_dir_blocks)

    return file_system

def get_file_system(f, root_dir_blocks, block_size, fat, root_dir_start):
    '''
        Return file system where keys are all directories with absolute paths
    '''
    file_system = dict()
    
    root_blocks = get_linked_blocks(f, root_dir_blocks, block_size, root_dir_start, fat)
    root_entries = get_directory(root_blocks, block_size, root_dir_blocks)
    file_entries = [file for file in root_entries if file['status'] == 3]
    subdir_entries = [dir for dir in root_entries if dir['status'] == 5]

    files = {}
    for file in file_entries:
        files[file['file_name']] = get_linked_blocks(f, file   ['num_blocks'], block_size, file['start_block'], fat)

    file_system['/'] = {
                            'entries': root_entries,
                            'files': files
                        }

    file_system = get_subdirs(f, file_system, subdir_entries, '/', block_size, fat, root_dir_blocks)

    return file_system

def print_entries(entries):
    for entry in entries:
        if entry['status'] == 3:
            file_type = "F"

        # subdirectory
        elif entry['status'] == 5:
            file_type = "D"

        # neither file nor directory
        else:
            return 0

        file_size = f"{entry['file_size']:>10}"
        file_name = entry['file_name'].strip('\x00')
        file_name = f"{file_name:>30}"
        creation_time = entry['creation_time']

        print(f"{file_type} {file_size} {file_name} {creation_time}")

def write_file_to_disk(f, file_data, fat, block_size, root_dir_start, root_dir_blocks):
    '''
        Write a file to the blocks on disk
    '''
    # Calculate the number of blocks needed
    num_blocks_needed = (len(file_data) + block_size - 1) // block_size

    # Find free blocks
    free_blocks = [k for k, v in fat.items() if v == 0x00][:num_blocks_needed]
    # print(free_blocks, num_blocks_needed)
    if len(free_blocks) < num_blocks_needed:
        raise Exception("Not enough free space on the disk")

    # Write data to the blocks
    for i, block in enumerate(free_blocks):
        f.seek(block * block_size)
        # print(f"Going to write at block {block}", file_data[i * block_size:(i + 1) * block_size])
        f.write(file_data[i * block_size:(i + 1) * block_size])

        # Update FAT in-memory (linking blocks)
        if i < len(free_blocks) - 1:
            fat[block] = free_blocks[i + 1]
        else:
            # Mark the last block in the FAT
            fat[block] = 0xFFFFFFFE  # End of file marker
    
    return free_blocks[0]

def update_fat(f, fat, fat_start, block_size):
    '''
        Update the FAT when writing a file to disk
    '''
    f.seek(fat_start * block_size)
    for entry in fat.values():
        # print(entry.to_bytes(4, byteorder='big'))
        f.write(entry.to_bytes(4, byteorder='big'))

def update_directory(f, destination_path, file_data, start_block, block_size, file_system, root_dir_start, root_dir_blocks):
    '''
        Update the directory entry when writing a file to disk
    '''
    # Split the destination path to get directory and filename
    path_parts = destination_path.split('/')
    dir_path = '/'.join(path_parts[:-2])
    the_dir = path_parts[-2]
    file_name = path_parts[-1]

    # Find the directory entry
    if dir_path == '':
        dir_path = '/'

        # print(file_system[dir_path]['entries'])
        directory_entry = {'start_block': root_dir_start, 'num_blocks': root_dir_blocks, 'file_name': '/'}
    else:
        directory_entry = [x for x in file_system[dir_path]['entries'] if x['file_name'] == the_dir][0]

    f.seek(directory_entry['start_block'] * block_size)
    status = -1
    while status != 0:
        status = int.from_bytes(f.read(1), 'big')
        if status != 0:
            f.read(63)

    # seek back one byte, so we put the file entry in the right place
    f.seek(-1, 1)
    
    # write in a 3 for status 
    f.write(b'\x03')

    f.write(start_block.to_bytes(4, byteorder='big'))

    num_blocks = (len(file_data) + block_size - 1) // block_size
    f.write(num_blocks.to_bytes(4, byteorder='big'))

    file_size = len(file_data)
    f.write(file_size.to_bytes(4, byteorder='big'))

    current_time = time.localtime()
    year, month, day, hour, minute, second = current_time.tm_year, current_time.tm_mon, current_time.tm_mday, current_time.tm_hour, current_time.tm_min, current_time.tm_sec
    # Write creation times
    f.write(year.to_bytes(2, byteorder='big'))
    f.write(month.to_bytes(1, byteorder='big'))
    f.write(day.to_bytes(1, byteorder='big'))
    f.write(hour.to_bytes(1, byteorder='big'))
    f.write(minute.to_bytes(1, byteorder='big'))
    f.write(second.to_bytes(1, byteorder='big'))
    # Modification times
    f.write(year.to_bytes(2, byteorder='big'))
    f.write(month.to_bytes(1, byteorder='big'))
    f.write(day.to_bytes(1, byteorder='big'))
    f.write(hour.to_bytes(1, byteorder='big'))
    f.write(minute.to_bytes(1, byteorder='big'))
    f.write(second.to_bytes(1, byteorder='big'))

    filename_bytes = file_name.encode('utf-8')
    # Ensure that the filename does not exceed 31 bytes
    if len(filename_bytes) > 31:
        raise ValueError("Filename is too long.")
    null_bytes_needed = 31 - len(filename_bytes)

    f.write(filename_bytes)
    f.write(b'\x00' * null_bytes_needed)

    filler = b'\xFF' * 6
    f.write(filler)