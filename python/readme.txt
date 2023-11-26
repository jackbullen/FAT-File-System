# Required for class assignment

- diskinfo: Get information

    1. Call `get_boot_sector` and print the information from here
    2. Then call `get_fat_info` with verbose=True

- disklist: List a directories contents

    1. Read the boot sector and fat info
    2. Call `get_file_system` and pass then correct dir into `print_entries`

- diskget: Write file from disk into local

    1.
    2.

- diskput: Write file from local into disk

# Additional routines

- diskinit: Create a disk (can be setup from a <disk_name>.initimg file)

- diskwipe: Wipe all blocks on the disk

- diskcopy: Copies the entire disk to local


- diskformat: Format a disk

- diskfix: Fix a disk

- diskcopy: Copy a disk

- diskdebug: Debug a disk

- diskdefrag: Defrag a disk

- diskrecover: Recover a disk