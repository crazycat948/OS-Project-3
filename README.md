# OS-Project-3
CS4348 Project 3: B-Tree Index File Manager
This project implements a disk-based B-Tree index file system for managing key-value pairs in a structured and scalable way. Designed as part of the CS4348 Operating Systems course, the program simulates block-level disk access using 512-byte blocks and supports command-line operations like inserting, searching, and printing data.

Features
Disk-based B-Tree structure with minimal memory footprint

Fixed 512-byte node and header blocks

Custom binary index file format

Insert key-value pairs with node splitting

Search for keys and return values

Print all key-value pairs in sorted order (in-order traversal)

File Structure
pgsql
Copy
Edit
.
├── main.py         # Command-line interface
├── fileio.py       # Handles block read/write, integer encoding
├── btree.py        # B-Tree logic: insert, search, print
├── README.md       # You're reading it!
Commands
Run everything with python main.py followed by a command.

Create a new index file
bash
Copy
Edit
python main.py create tree.idx
Insert key-value pair
bash
Copy
Edit
python main.py insert tree.idx 42 1234
Search for a key
bash
Copy
Edit
python main.py search tree.idx 42
# Output: Found key: 42, value: 1234
Print all key-value pairs (sorted)
bash
Copy
Edit
python main.py print tree.idx
# Output:
# Key: 10, Value: 100
# Key: 20, Value: 200
# ...
File Format
Header (Block 0)
Offset	Description
0–7	Magic number 4348PRJ3
8–15	Root node block ID
16–23	Next available block ID

B-Tree Node (Each 512-byte block)
Field	Count	Bytes
Block ID	1	8
Parent Block ID	1	8
Number of keys	1	8
Keys	19	152
Values	19	152
Children (pointers)	20	160

Technical Notes
All integers are stored as 8-byte big-endian values.

Only 3 nodes are held in memory at any time.

The B-Tree has minimum degree = 10, allowing up to 19 keys per node.

Built using Python 2/3 compatible syntax with struct for binary packing.

Future Enhancements
load: Bulk insert from CSV

extract: Export all key-value pairs to CSV

Internal node splitting (beyond root)

Delete operation (not required in this assignment)

Author
Yifan Ren
CS4348 – Operating Systems (Spring 2025)
The University of Texas at Dallas
