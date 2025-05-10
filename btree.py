from fileio import int_to_bytes, bytes_to_int, read_block, write_block, build_header, parse_header
import os
import csv


class BTreeNode:
    def __init__(self, block_id, parent_id=0, num_keys=0):
        self.block_id = block_id
        self.parent_id = parent_id
        self.num_keys = num_keys
        self.keys = [0] * 19
        self.values = [0] * 19
        self.children = [0] * 20

    def to_bytes(self):
        data = bytearray()
        data += int_to_bytes(self.block_id)
        data += int_to_bytes(self.parent_id)
        data += int_to_bytes(self.num_keys)
        for i in range(19):
            data += int_to_bytes(self.keys[i])
        for i in range(19):
            data += int_to_bytes(self.values[i])
        for i in range(20):
            data += int_to_bytes(self.children[i])
        return data.ljust(512, b'\x00')

    @staticmethod
    def from_bytes(data):
        block_id = bytes_to_int(data[0:8])
        parent_id = bytes_to_int(data[8:16])
        num_keys = bytes_to_int(data[16:24])
        node = BTreeNode(block_id, parent_id, num_keys)
        offset = 24
        for i in range(19):
            node.keys[i] = bytes_to_int(data[offset:offset+8])
            offset += 8
        for i in range(19):
            node.values[i] = bytes_to_int(data[offset:offset+8])
            offset += 8
        for i in range(20):
            node.children[i] = bytes_to_int(data[offset:offset+8])
            offset += 8
        return node

def insert(filename, key, value):
    with open(filename, 'rb+') as f:
        header_data = read_block(f, 0)
        root_id, next_id = parse_header(header_data)

        if root_id == 0:
            root_node = BTreeNode(block_id=next_id)
            root_node.keys[0] = key
            root_node.values[0] = value
            root_node.num_keys = 1
            write_block(f, root_node.block_id, root_node.to_bytes())
            new_header = build_header(root_id=next_id, next_block_id=next_id + 1)
            write_block(f, 0, new_header)
            print("Inserted into new root.")
            return

        root_data = read_block(f, root_id)
        root = BTreeNode.from_bytes(root_data)

        if root.num_keys < 19:
            i = root.num_keys
            root.keys[i] = key
            root.values[i] = value
            root.num_keys += 1
            zipped = sorted(zip(root.keys[:root.num_keys], root.values[:root.num_keys]))
            for j in range(root.num_keys):
                root.keys[j], root.values[j] = zipped[j]
            write_block(f, root.block_id, root.to_bytes())
            print("Inserted into existing root.")
        else:
            new_root_id, new_next_id = split_node(f, root, key, value, (root_id, next_id))
            new_header = build_header(root_id=new_root_id, next_block_id=new_next_id)
            write_block(f, 0, new_header)
            print("Root split. New root is block {}.".format(new_root_id))

def split_node(f, node, key, value, header):
    root_id, next_id = header
    all_pairs = list(zip(node.keys[:node.num_keys], node.values[:node.num_keys]))
    all_pairs.append((key, value))
    all_pairs.sort()

    left_pairs = all_pairs[:9]
    promoted_pair = all_pairs[9]
    right_pairs = all_pairs[10:]

    left_node = BTreeNode(block_id=node.block_id)
    for i, (k, v) in enumerate(left_pairs):
        left_node.keys[i] = k
        left_node.values[i] = v
    left_node.num_keys = len(left_pairs)

    right_node = BTreeNode(block_id=next_id)
    for i, (k, v) in enumerate(right_pairs):
        right_node.keys[i] = k
        right_node.values[i] = v
    right_node.num_keys = len(right_pairs)
    next_id += 1

    new_root = BTreeNode(block_id=next_id)
    new_root.keys[0] = promoted_pair[0]
    new_root.values[0] = promoted_pair[1]
    new_root.children[0] = left_node.block_id
    new_root.children[1] = right_node.block_id
    new_root.num_keys = 1
    next_id += 1

    left_node.parent_id = new_root.block_id
    right_node.parent_id = new_root.block_id

    write_block(f, left_node.block_id, left_node.to_bytes())
    write_block(f, right_node.block_id, right_node.to_bytes())
    write_block(f, new_root.block_id, new_root.to_bytes())

    return new_root.block_id, next_id

def search(filename, key):
    with open(filename, 'rb') as f:
        header_data = read_block(f, 0)
        root_id, _ = parse_header(header_data)

        if root_id == 0:
            print("Tree is empty.")
            return

        node_id = root_id

        while node_id != 0:
            data = read_block(f, node_id)
            node = BTreeNode.from_bytes(data)

            for i in range(node.num_keys):
                if key == node.keys[i]:
                    print("Found key: {}, value: {}".format(key, node.values[i]))
                    return
                elif key < node.keys[i]:
                    node_id = node.children[i]
                    break
            else:
                node_id = node.children[node.num_keys]

        print("Key {} not found.".format(key))

def print_tree(filename):
    with open(filename, 'rb') as f:
        header_data = read_block(f, 0)
        root_id, _ = parse_header(header_data)

        if root_id == 0:
            print("Tree is empty.")
            return

        def in_order(node_id):
            if node_id == 0:
                return

            data = read_block(f, node_id)
            node = BTreeNode.from_bytes(data)

            for i in range(node.num_keys):
                in_order(node.children[i])
                print("Key: {}, Value: {}".format(node.keys[i], node.values[i]))
            in_order(node.children[node.num_keys])

        in_order(root_id)
        
        
def load(filename, csv_filename):

    if not os.path.exists(filename):
        print("Error: Index file '{}' does not exist.".format(filename))
        return

    if not os.path.exists(csv_filename):
        print("Error: CSV file '{}' does not exist.".format(csv_filename))
        return

    with open(csv_filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        line_num = 0
        for row in reader:
            line_num += 1
            if len(row) != 2:
                print("Warning: Line {} malformed, skipping.".format(line_num))
                continue
            try:
                key = int(row[0].strip())
                value = int(row[1].strip())
                insert(filename, key, value)
            except ValueError:
                print("Warning: Line {} has invalid integers, skipping.".format(line_num))
                
                
def extract(filename, output_csv):
    import csv

    if not os.path.exists(filename):
        print("Error: Index file '{}' does not exist.".format(filename))
        return

    if os.path.exists(output_csv):
        print("Error: Output file '{}' already exists.".format(output_csv))
        return

    with open(filename, 'rb') as f, open(output_csv, 'w', newline='') as out:
        writer = csv.writer(out)
        header_data = read_block(f, 0)
        root_id, _ = parse_header(header_data)

        if root_id == 0:
            print("Tree is empty. Nothing to extract.")
            return

        def in_order(node_id):
            if node_id == 0:
                return

            data = read_block(f, node_id)
            node = BTreeNode.from_bytes(data)

            for i in range(node.num_keys):
                in_order(node.children[i])
                writer.writerow([node.keys[i], node.values[i]])
            in_order(node.children[node.num_keys])

        in_order(root_id)
    print("Extraction complete: all entries written to '{}'.".format(output_csv))