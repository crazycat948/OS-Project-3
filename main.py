import sys
import os
from fileio import build_header, write_block
from btree import insert, search, print_tree, load, extract

def create_index_file(filename):
    if os.path.exists(filename):
        print("Error: File '{}' already exists.".format(filename))
        return
    with open(filename, 'wb') as f:
        header_block = build_header()
        write_block(f, 0, header_block)
    print("Index file '{}' created successfully.".format(filename))

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 main.py <command> <filename> [args]")
        return

    command = sys.argv[1]
    filename = sys.argv[2]

    if command == "create":
        create_index_file(filename)

    elif command == "insert":
        if len(sys.argv) != 5:
            print("Usage: python3 main.py insert <filename> <key> <value>")
            return
        key = int(sys.argv[3])
        value = int(sys.argv[4])
        insert(filename, key, value)

    elif command == "search":
        if len(sys.argv) != 4:
            print("Usage: python3 main.py search <filename> <key>")
            return
        key = int(sys.argv[3])
        search(filename, key)

    elif command == "print":
        if len(sys.argv) != 3:
            print("Usage: python3 main.py print <filename>")
            return
        print_tree(filename)

    elif command == "load":
        if len(sys.argv) != 4:
            print("Usage: python3 main.py load <index_file> <csv_file>")
            return
        csv_file = sys.argv[3]
        load(filename, csv_file)
        
    elif command == "extract":
        if len(sys.argv) != 4:
            print("Usage: python3 main.py extract <index_file> <output_csv>")
            return
        output_file = sys.argv[3]
        extract(filename, output_file)

    else:
        print("Unknown command '{}'".format(command))

if __name__ == "__main__":
    main()
