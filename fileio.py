import struct

BLOCK_SIZE = 512
INT_SIZE = 8
MAGIC = b"4348PRJ3"

def int_to_bytes(n):
    return struct.pack('>Q', n)

def bytes_to_int(b):
    return struct.unpack('>Q', b)[0]

def read_block(file, block_id):
    file.seek(block_id * BLOCK_SIZE)
    data = file.read(BLOCK_SIZE)
    if len(data) < BLOCK_SIZE:
        data += b'\x00' * (BLOCK_SIZE - len(data))
    return data

def write_block(file, block_id, data):
    if len(data) > BLOCK_SIZE:
        raise ValueError("Block too large")
    file.seek(block_id * BLOCK_SIZE)
    file.write(data.ljust(BLOCK_SIZE, b'\x00'))

def build_header(root_id=0, next_block_id=1):
    data = bytearray()
    data += MAGIC
    data += int_to_bytes(root_id)
    data += int_to_bytes(next_block_id)
    return data.ljust(512, b'\x00')

def parse_header(data):
    if data[:8] != MAGIC:
        raise ValueError("Invalid index file: magic mismatch")
    root_id = bytes_to_int(data[8:16])
    next_block_id = bytes_to_int(data[16:24])
    return root_id, next_block_id