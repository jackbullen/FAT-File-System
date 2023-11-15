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

def get_fat_info(f, fat_start, fat_blocks, block_size, root, verbose=False) -> dict:
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
    for i in range(root_dir_blocks):
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
        root[i] = {
            'status':status, 
            'filename': filename, 
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