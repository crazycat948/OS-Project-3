CS4348 Project 3: B-Tree Index File Manager
This project implements a command-line program that creates and manages a disk-based B-Tree index file using fixed-size 512-byte blocks. The index supports key-value insertion, searching, printing, loading from a CSV file, and extracting to a CSV file.

This was developed for the CS4348 Operating Systems course at The University of Texas at Dallas.

How to Run
Use Python 3 to run the program. Example:

python3 main.py <command> <filename> [args]
Available Commands

1. Create
Creates a new index file. Fails if the file already exists.

python3 main.py create <index_file>

Example:

python3 main.py create tree.idx

2. Insert
Inserts a single key-value pair into the index file.
python3 main.py insert <index_file> <key> <value>
Example:
python3 main.py insert tree.idx 10 100

3. Search

Searches for a specific key and prints the value if found.
python3 main.py search <index_file> <key>

Example:
python3 main.py search tree.idx 10

4. Print
Prints all key-value pairs in sorted order.

python3 main.py print <index_file>
Example:
python3 main.py print tree.idx

5. Load (from CSV)
Loads and inserts key-value pairs from a CSV file. Each line in the CSV must have the format:
key,value
Command:
python3 main.py load <index_file> <input_csv_file>
Example:
python3 main.py load tree.idx input.csv

6. Extract (to CSV)
Exports all key-value pairs in sorted order to a new CSV file. Fails if the file already exists.
python3 main.py extract <index_file> <output_csv_file>
Example:
python3 main.py extract tree.idx output.csv

Notes
All data is stored in 512-byte blocks using big-endian format.

The B-Tree has a minimum degree of 10 and supports up to 19 key-value pairs per node.

The program only loads a maximum of 3 nodes into memory at any time.

