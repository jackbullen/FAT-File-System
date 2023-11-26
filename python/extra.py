"""
    Extra python codes that could be useful
"""

# 1.
######

# Getting file contents

# if entry["num_blocks"] > 1:
#     a = get_block(f, entry['start_block'], block_size)
#     f.seek(fat_start*block_size + entry['start_block']*4, 0)
#     curr = int.from_bytes(f.read(4), 'big')
#     a += get_block(f, curr, block_size)
#     while curr != 0xffffffff:
#         curr = fat[curr]
#         a += get_block(f, curr, block_size)