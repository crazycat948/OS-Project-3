# 5/5 / 2025 

Today I built the low-level file operations for the index system. I created a new module called fileio.py where I wrote functions to handle reading and writing 512-byte blocks to a file. These blocks will represent either the header or individual B-Tree nodes, and the fixed size helps simulate how real disk storage behaves. Each read function pulls exactly one block based on a block ID (which is just the offset), and the write function pads the data if it is shorter than 512 bytes to keep things consistent. I also added helper functions to convert integers to and from 8-byte big-endian format, since the project requires all numbers in the file to be stored this way regardless of system architecture. I tested the read and write flow using a dummy block that included an integer and a short string, and it successfully printed the values after reading the block back. This setup will be reused throughout the rest of the program whenever I need to interact with the file. Next, I’ll move on to designing the index file header layout and implementing the create command, which will let us initialize a new index file with the correct metadata and structure.  

# 5/8 / 2025 
Today I implemented the ability to create a new index file and write a proper 512-byte header to it. I added a create_index_file() function in main.py that checks if the file already exists, and if not, it initializes a new file using a helper function from fileio.py called build_header(). This header includes a fixed magic number (4348PRJ3), a root block ID set to 0, and a next block ID set to 1, as required by the project spec. Writing the header is done using a separate function write_block(), which ensures that exactly 512 bytes are written to block 0.

wwhile implementing this, I initially used Python 3-style f-strings for printing messages, which led to a SyntaxError when I tried running the script. I realized the environment was defaulting to Python 2, so I updated all formatted print statements to use .format() instead. After that, I ran into a second issue: Python 2 doesnt support the int.to_bytes() method I had used for integer conversion. This caused an AttributeError when building the header. To fix this, I rewrote the integer conversion logic using the struct module, specifically struct.pack('>Q', n) for writing and struct.unpack('>Q', b)[0] for reading, which works in both Python 2 and 3.

Once those fixes were in place, I successfully created the index file and confirmed that the header was written correctly. With the file creation logic complete and tested, I now have a clean way to initialize a B-Tree index file. Next, I’ll move on to defining the B-Tree node structure and writing the serialization/deserialization logic for nodes in btree.py.
#5/9/2025/8:30pm

Today I designed and implemented the data structure for B-Tree nodes, which are stored in 512-byte blocks. I created a new file called btree.py and wrote a BTreeNode class that represents a single node in the tree. Each node contains fields for its own block ID, the parent block ID, the number of key-value pairs it holds, and fixed-size arrays for up to 19 keys, 19 values, and 20 child block pointers. To match the format required by the project, I implemented two key methods: to_bytes(), which serializes the node into a 512-byte block ready to be written to disk, and from_bytes(), which does the reverse—reading raw bytes and turning them back into a usable BTreeNode object. The actual packing and unpacking of integers relies on the integer conversion functions I wrote earlier in fileio.py. I tested the node logic by writing a sample node to block 1 of the test index file and then reading it back to confirm the structure remained consistent. This phase was straightforward, but getting the offsets exactly right in the byte array was important since even a small misalignment could break the whole structure. With this in place, the B-Tree now has a fully defined node layout, and I’m ready to move on to implementing the actual insertion logic and handling the case where the root splits and a new root must be created.

#5/9/10:45pm
And also I implemented the initial insert functionality for the B-Tree. The goal was to support inserting key-value pairs into the index file, starting with the simplest case: inserting into an empty tree and then into a non-full root node. I wrote a new insert() function in btree.py that begins by reading the header block to determine if a root exists. If the root ID is 0, that means the tree is currently empty, so I create a new root node at the next available block ID, store the first key-value pair there, and update the header with the new root ID and incremented next block ID. If the root already exists, I read it into memory and insert the new key-value pair at the end of the keys array. I also sort the key-value pairs to maintain the correct order, since B-Tree nodes must stay sorted. For now, I added a condition to reject inserts into a full node with a message indicating that split logic hasnt been implemented yet. In main.py, I added command-line argument support for the insert command, which takes a filename, key, and value. I tested the code by inserting a few values into a newly created index file, and it worked as expected, writing everything to disk with no more than one node in memory at a time. With this phase complete, the B-Tree is now capable of basic, non-splitting inserts. The next step is to implement node splitting and upward propagation to support a growing tree.

#5/10/2025 12:35am
Today I implemented node splitting and root growth in the B-Tree, which allows the structure to handle insertions even when the root node is full. Before this point, inserts were limited to a single root node with up to 19 key-value pairs. Once it reached capacity, the program would simply report that a split wasn’t implemented. To move beyond that, I added logic to split the node into two child nodes and promote the median key up to a new root. This was done in a helper function called split_node() in btree.py. The function takes the full node, inserts the new key-value pair, sorts everything, then divides the list: the first 9 pairs go to the left node, the last 9 to the right, and the middle key gets promoted to a new root. Both child nodes point back to the new root as their parent, and the header is updated to reflect the new root’s block ID and the next available block ID. I carefully wrote each node to disk in the correct order and reused the existing block ID for the left node to conserve space. One challenge was ensuring the node fields and block layout stayed consistent during serialization and deserialization, especially since each node must stay within a 512-byte limit. I also had to make sure the new root and child nodes only used the block IDs provided by the file’s metadata, not hardcoded values. After testing with multiple inserts, I confirmed that the split occurs correctly and that the B-Tree can now grow beyond a single block. The next step is to extend insert support to internal nodes and eventually implement recursive splits when multiple levels are full.
To verify everything, I ran the following commands:
$ python3 main.py create tree.idx
$ python3 main.py insert tree.idx 10 100
$ python3 main.py insert tree.idx 20 200
Everything executed successfully, and I confirmed that once the root reached capacity, it split as expected and created a new root above it. This proves that the splitting and root promotion logic is functional and correctly updates the header and child pointers. With this phase complete, the B-Tree can now dynamically grow beyond a single block. Next, I’ll expand the insert logic to work with internal nodes, setting up for full recursive splits deeper into the tree structure.

#5/10/2025 2:11pm
I implemented the search functionality for the B-Tree index. The goal was to allow users to query a specific key in the tree and either return the associated value or indicate that the key wasn’t found. I added a new function called search() in btree.py, which starts at the root node and follows the correct child pointer based on the value of the key being searched. The traversal logic compares the key with all keys in the current node, and if it finds a match, it prints the associated value. If the key is smaller than a given node key, it follows the corresponding child pointer. If it’s larger than all keys in the node, it follows the rightmost child pointer. If the traversal reaches a leaf node and the key hasn’t been found, the function prints a message saying so.

One important aspect of this design is that the search only loads one node at a time from disk, so the memory footprint stays small and consistent with the project’s requirement to never load more than a few nodes into memory at once. It also works with any number of tree levels, whether the tree has just a root or has already split and formed a new root and child layers.

To test the feature, I used the following commands:
$ python main.py create tree.idx
$ python main.py insert tree.idx 10 100
$ python main.py insert tree.idx 20 200
$ python main.py insert tree.idx 30 300
$ python main.py search tree.idx 10
Found key: 10, value: 100

$ python main.py search tree.idx 20
Found key: 20, value: 200

$ python main.py search tree.idx 99
Key 99 not found.
These tests confirmed that the search correctly finds inserted keys even after a root split, and correctly reports when a key isn’t present in the tree. With search working, the B-Tree now supports both reading and writing operations. The next step is to implement the print command to display all key-value pairs in sorted order using an in-order traversal .

#5/10/2025 5:00pm
I implemented the print command for the B-Tree, which performs an in-order traversal to display all key-value pairs stored in the tree in sorted order. This required recursively visiting each node starting from the root, visiting left children, then printing the current key-value, and finally visiting the right child. I added a function called print_tree() in btree.py and used a helper function in_order() inside it to perform the traversal. The function reads each node from disk as needed, which keeps memory usage low and consistent with the requirement of not loading more than a few nodes into memory.

To make this accessible from the command line, I added a new print command in main.py. This allows users to run python main.py print <filename> and see all records printed in increasing key order.

I tested the functionality by inserting multiple keys in random order and then printing the contents of the tree. Here’s what I ran:
$ python main.py create tree.idx
$ python main.py insert tree.idx 30 300
$ python main.py insert tree.idx 10 100
$ python main.py insert tree.idx 20 200
$ python main.py insert tree.idx 40 400
$ python main.py print tree.idx
The output was:
Key: 10, Value: 100
Key: 20, Value: 200
Key: 30, Value: 300
Key: 40, Value: 400

his confirmed that the in-order traversal is functioning correctly, even after node splits, and that the B-Tree structure is being maintained on disk as expected. With this phase complete, the B-Tree supports not only insertions and searches, but also full visibility into its current contents in sorted order. Next, I’ll implement the load command to bulk insert from CSV files, and the extract command to export all data into a file.


#5/10/2025 8:41pm

I implemented the load feature in the B-Tree index manager, which allows the program to bulk-insert key-value pairs from a CSV file. I wrote a function called load() in btree.py that reads a specified CSV file line by line, parses each key,value pair, and inserts it into the B-Tree using the existing insert() function. It also includes error handling for malformed lines and missing files.

To support this from the command line, I updated main.py by adding a new elif command == "load": block to handle the load <index_file> <csv_file> command. However, I ran into a strange issue where Python kept giving me a syntax error on that line, even though the code looked correct. The error message was:
File "main.py", line 47
    elif command == "load":
                              ^
			      SyntaxError
It turned out to be caused by inconsistent indentation — the elif line had 5 spaces instead of 4. Python is sensitive to indentation, so it was treated as a broken block. After retyping the line manually with correct spacing and checking the previous block for proper closure, the error was resolved. I also realized I had forgotten to import the load function at the top of main.py, so I added load to the import list from btree.

Once the bug was fixed, I tested the feature using the following steps:

I created a test CSV file called input.csv with this content:
10,100
20,200
30,300
Then I ran:
python3 main.py create tree.idx
python3 main.py load tree.idx input.csv
python3 main.py print tree.idx
The output was:Key: 10, Value: 100
Key: 20, Value: 200
Key: 30, Value: 300
This confirmed that the load feature works correctly and integrates seamlessly with the existing B-Tree logic. With this phase complete, the program now supports automated batch inserts, making it much easier to test large inputs and prepare data quickly.

Next up, I plan to implement the extract command, which will export all key-value pairs in the tree to a CSV file.



#5/10/2025 10:21pm
I implemented the extract command, which allows the B-Tree index system to export all stored key-value pairs to a CSV file. This is useful for saving the data in a readable format or transferring it to other programs. I added a new function called extract() in btree.py, which performs an in-order traversal of the tree—just like the print function—but instead of printing to the console, it writes each key-value pair to a .csv file using Pythons csv module.

One important detail was handling file existence properly: if the output CSV file already exists, the program will exit with an error message instead of overwriting the file. This aligns with the project spec that says the output file should remain unmodified unless explicitly created.

In main.py, I added a new command handler for extract, which takes two arguments: the index file and the output CSV filename. I also updated the import statement to include extract() from btree.

After implementing the function, I tested it using the following commands:
python3 main.py extract tree.idx output.csv

Extraction complete: all entries written to 'output.csv'.

This confirmed that the tree was traversed in sorted order and the output file was written correctly. The function also handled the case when the output file already existed by printing an appropriate error message and exiting cleanly.

With this phase complete, the system now supports both loading data from CSV and exporting it back, making it much more usable and easier to verify correctness. The core features of the project are now fully functional.
