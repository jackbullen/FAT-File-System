use std::env;
use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::str;

const BOOT_SECTOR_SIZE: usize = 512;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        eprintln!("Usage: ./diskinfo <image_file>");
        std::process::exit(1);
    }

    let filename = &args[1];

    let mut file = File::open(filename).expect("Error: Failed to open file");

    let mut boot_sector = [0u8; BOOT_SECTOR_SIZE];

    file.read_exact(&mut boot_sector).expect("Failed to read boot sector");

    let block_size = u16::from_be_bytes([boot_sector[8], boot_sector[9]]) as usize;
    let block_count = u32::from_be_bytes([boot_sector[10], boot_sector[11], boot_sector[12], boot_sector[13]]) as usize;
    
    let fat_start = u32:: from_be_bytes([boot_sector[14], boot_sector[15], boot_sector[16], boot_sector[17]]) as usize;
    let fat_blocks = u32::from_be_bytes([boot_sector[18], boot_sector[19], boot_sector[20], boot_sector[21]]) as usize;

    let block_root_dir_start = u32::from_be_bytes([boot_sector[22], boot_sector[23], boot_sector[24], boot_sector[25]]);
    let block_root_dir_blocks = u32::from_be_bytes([boot_sector[26], boot_sector[27], boot_sector[28], boot_sector[29]]);

    let root_dir_start = fat_start + fat_blocks;
    let root_dir_blocks = block_count / block_size;

    let os_name = str::from_utf8(&boot_sector[0..7]).expect("Failed to parse OS name");

    println!("OS Name: {}", os_name);
    println!("Total size of the disk: {} bytes", block_size * block_count);
    println!("===============");
    println!("Super block information:");
    println!("===============");
    println!("Block size: {} bytes", block_size);
    println!("Block count: {}", block_count);
    println!("FAT starts: {}", fat_start);
    println!("FAT blocks: {}", fat_blocks);
    println!("Root directory start: {}", root_dir_start);
    println!("block root dir start: {}", block_root_dir_start);
    println!("Root directory blocks: {}", root_dir_blocks);
    println!("block root dir blocks: {}", block_root_dir_blocks);
    println!("===============");

    let mut free_blocks = 0;
    let mut reserved_blocks = 0;
    let mut allocated_blocks = 0;

    file.seek(SeekFrom::Start((fat_start * block_size) as u64)).expect("Failed to seek to FAT");

    for i in 0..(block_count) {
        let mut fat_entry = [0u8; 2];
        file.read_exact(&mut fat_entry).expect("Failed to read FAT entry");

        let entry_value = u16::from_le_bytes(fat_entry);

        match entry_value {
            0x00 => free_blocks += 1,
            0xFF00..=0xFFFF => reserved_blocks += 1,
            _ => {
                allocated_blocks += 1;

                let start_pos = i * block_size;
                file.seek(SeekFrom::Start(start_pos as u64)).expect("Failed to seek to block");

                let mut block_content = vec![0u8; block_size as usize];
                file.read_exact(&mut block_content).expect("Failed to read block");

                if let Ok(decoded_str) = String::from_utf8(block_content) {
                    println!("Block {}: {}", i, decoded_str);
                } else {
                    println!("Block {} contains invalid UTF-8 data", i);
                }
            }
        }
    }

    println!("Free Blocks: {}", free_blocks);
    println!("Reserved Blocks: {}", reserved_blocks);
    println!("Allocated Blocks: {}", allocated_blocks);

}