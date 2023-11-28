## Here is an explanation of each of the source files in python directory
---

- **utils.py:**

    Contains most of the code for routines, used to simplify the other files
    Included functions:

        1. `get_boot_sector(f)`
        --------------------- 
        -> `os_name, block_size, block_count, fat_start, fat_blocks, root_dir_start, root_dir_blocks`

            get_boot_sector reads the super blocks


        2. `get_fat_info(f, fat_start, fat_blocks, block_size, verbose=False)`
        --------------------------------------------------------------------
        -> `file_access_table`

            get_fat_info reads the FAT. If verbose is set True
            it will print the superblock free/reserved/allocated
            counts.


        3. `get_block(f, block_number, block_size)`
        -----------------------------------------
        -> `f.read(block_size)`

            get_block simply returns the block at block_number.


        4. `get_directory(dir_bytes, block_size, root_dir_blocks)`
        --------------------------------------------------------
        -> `entries`

            get_directory returns a dictionary containing the entries
            inside of this dictionary data blocks


        5. `get_linked_blocks(f, num_blocks, block_size, dir_start, fat)`
        ---------------------------------------------------------------
        -> `file`

            get_linked_blocks returns num_blocks blocks linked in
            the fat, starting from dir_start.


        6. `get_subdirs(f, file_system, subdirs, parent, block_size, fat, root_dir_blocks)`
        ---------------------------------------------------------------------------------
        -> `file_system`

            get_subdirs recursively calls itself on all dirs inside of subdirs.


        7. `get_file_system(f, root_dir_blocks, block_size, fat, root_dir_start)`
        -----------------------------------------------------------------------
        -> `file_system`

            get_file_system calls get_subdirs recursively to get a dictionary whose
            keys are the all directory paths in the file system. For example, in
            subdirs.img has keys: "/", "/subdir1", and "/subdir1/subdir2/. Each
            dictionary entry contains another dictionary whose keys are "entries"
            and "files". "entries" includes the directory lookup information for 
            everything (files and dirs) inside of this path. "files" contains a
            list with all of the files data.

        
        8. `print_entries(entries)`
        -------------------------
        -> `None`

            print_entries prints the dir entries as required.

        
        9. `write_file_to_disk(f, file_data, fat, block_size, root_dir_start, root_dir_blocks)`
        -------------------------------------------------------------------------------------
        -> `free_blocks[0]`

            Writes file_data into the first free block and returns index of first block.


        10. `update_fat(f, fat, fat_start, block_size)`
        ---------------------------------------------
        -> `None`

            Writes the new FAT lookups.


        11. `update_directory(f, destination_path, file_data, start_block, block_size, file_system, root_dir_start, root_dir_blocks)`
        ---------------------------------------------------------------------------------------------------------------------------
        -> `None`

            Writes the new directory entry into the directory blocks.


- **diskinfo.py**

    Calls get_boot_sector and get_fat_info.

- **disklist.py**

    Calls get_file_system, parses the input dir, and calls print_entries with the entries.

- **diskget.py**

    Calls get_file_system, parses the input file and path, writes the file data to local.

- **diskput.py**

    1. Write the file to image 2. Update the FAT 3. Update the directory.

- **diskrm.py**
    
    Removes files from the image file.

- **make_submission.py**

    Calls diskput on all python files.

- **make_p3_image.sh**

    Call make, cleans the test.img by calling diskrm on all files, then calls make_submission.py and make clean.