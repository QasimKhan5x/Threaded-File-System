# Threaded-File-System
Logical file system that implements paging, multithreading, etc.


### Notes
1. If a thread opens a file for modification, the changes it makes will not be saved until it closes the file.
2. Reading a file's contents is already thread safe (point 3 touches this further).
3. A thread cannot read the updated contents of a file until the writer thread has closed the file.
4. A file is **locked** for modification by a single thread.
