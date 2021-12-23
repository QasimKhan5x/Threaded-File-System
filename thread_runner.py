from util import *


def thread_runner(name, outfile, fs, commands):
    '''
    name: id of thread (instead of threading.get_ident() for simplicity)
    outfile: file path of output
    fs: FileSystem object
    commands: list of commands to perform
    '''
    thread_id = name
    # filename -> (file, current_contents)
    # used to store the reference to the file object
    # and the current contents (possibly modified in w mode)
    cache = {}
    for command in commands:
        tokens = command.split()
        # File System and Directory related Commands
        if command.startswith('mkdir'):
            dirname = tokens[-1]
            result = fs.mkdir(dirname)
            if type(result) != int:
                print2file(fs, outfile)
            else:
                if result == 0:
                    msg = "Duplicate directory. Operation ignored."
                else:
                    msg = "No such parent directory exists!"
                write2file(outfile, msg)
        elif command.startswith('chdir'):
            dirname = tokens[-1]
            result = fs.chdir(dirname)
            if result == 0:
                write2file(outfile, "No such directory exists!")
            else:
                write2file(outfile, fs.pwd())
        elif command.startswith('mv'):
            f1, f2 = tokens[1:]
            result = fs.mv(f1, f2)
            if type(result) == int:
                if result == 0:
                    msg = "Source file doesn't exist!"
                else:
                    msg = "Destination directory doesn't exist!"
                write2file(outfile, msg)
            else:
                print2file(fs, outfile)
        elif command.startswith('pwd'):
            write2file(outfile, fs.pwd())
        elif command.startswith('print'):
            print2file(fs, outfile)
        elif command.startswith('show_memory_map'):
            showmm2file(fs, outfile)
        elif command.startswith('save'):
            dst = tokens[-1]
            fs.save(dst)
            write2file(outfile, f'Filesystem saved at {dst}')
        # File I/O
        elif command.startswith('create'):
            fname = tokens[-1]
            result = fs.create(fname)
            if type(result) == int:
                if result == 0:
                    msg = "No such directory exists!"
                else:
                    msg = "Duplicate file. Operation ignored."
                write2file(outfile, msg)
            else:
                print2file(fs, outfile)
        elif command.startswith('delete'):
            fname = tokens[-1]
            result = fs.delete(fname)
            if result:
                print2file(fs, outfile)
            else:
                write2file(outfile, "No such file exists!")
        elif command.startswith('open'):
            fname, mode = tokens[1:]
            if mode == 'r':
                mode_msg = 'reading'
            elif mode == 'w':
                mode_msg = 'writing'
            else:
                # invalid mode
                continue
            file = fs.open(fname)
            if file == False:
                write2file(outfile, f"{fname} doesn't exist")
                continue
            if fname in global_file_table:
                # opening again without closing
                if thread_id in global_file_table[fname]:
                    write2file(
                        outfile, f"{fname} must be closed before opening it again")
                    continue
                '''
                More than one thread cannot open a file for writing
                The current thread must wait
                An implementation of locking:
                    If thread wants to write
                    Then check if another thread is writing to this file
                    Wait until that thread closes the file
                '''
                if mode == 'w':
                    while 'w' in global_file_table[fname].values():
                        continue
                # add this thread to the list of threads who have opened this file
                global_file_table[fname][thread_id] = mode
            else:
                global_file_table[fname] = {thread_id: mode}
            cache[fname] = (file, file.get_contents())
            write2file(outfile, f"{fname} opened for {mode_msg}")
        elif command.startswith('close'):
            fname = tokens[-1]
            file, contents = cache.pop(fname, (None, None))
            if file == None:
                write2file(
                    outfile, f"{fname} has not been opened / doesn't exist")
                continue
            result = fs.close(fname, contents)
            if result == 0:
                write2file(outfile, f"{fname} doesn't exist!")
                continue
            # remove association of thread with this file from GFT, if it exists
            if fname not in global_file_table:
                write2file(outfile,
                           f"BUG: {fname} exists in thread's cache but not in GFT")
                continue
            thread_list = global_file_table[fname]
            if thread_id not in thread_list:
                write2file(outfile, f"This thread has not opened {fname}")
                continue
            # if this was a writer thread, another writer thread trying to access
            # this file will not be blocked anymore
            del global_file_table[fname][thread_id]
            # remove this file from GFT if no threads have opened it
            if len(global_file_table[fname]) == 0:
                del global_file_table[fname]
            # python thinks 1 and True are the same so I have to use 'is' instead =_=
            if result is 1:
                write2file(
                    outfile, f"Not enough frames available to save changes made to {fname}")
            else:
                write2file(
                    outfile, f"{fname} has been closed and any changes made were saved.")
        elif command.startswith('read_from'):
            fname = tokens[1]
            start = int(tokens[2])
            size = int(tokens[3])
            if not assert_file_availability(fname, thread_id, cache, outfile, 'r'):
                continue
            file, _ = cache[fname]
            result = file.read_from(start, size)
            write2file(outfile, f'Contents of {fname}: {result}')
        elif command.startswith('read'):
            fname = tokens[1]
            if not assert_file_availability(fname, thread_id, cache, outfile, 'r'):
                continue
            file, _ = cache[fname]
            result = file.read()
            write2file(outfile, f'Contents of {fname}: {result}')
        elif command.startswith('append'):
            fname, text = tokens[1:]
            if not assert_file_availability(fname, thread_id, cache, outfile, 'w'):
                continue
            file, contents = cache[fname]
            new_contents = append(contents, text)
            cache[fname] = (file, new_contents)
            write2file(
                outfile, f'Append text {text} to {fname} committed as transaction.')
        elif command.startswith('write'):
            fname = tokens[1]
            text = tokens[2]
            pos = int(tokens[3])
            if not assert_file_availability(fname, thread_id, cache, outfile, 'w'):
                continue
            file, contents = cache[fname]
            new_contents = write_at(contents, pos, text)
            cache[fname] = (file, mode, new_contents)
            write2file(
                outfile, f'Append text {text} to {fname} committed as transaction.')
        elif command.startswith('move'):
            fname = tokens[1]
            if not assert_file_availability(fname, thread_id, cache, outfile, 'w'):
                continue
            # read tokens from position 2 onwards
            # map the items in the list to integers
            # cast to tuple and unpack it
            start, size, target = tuple(map(int, tokens[2:]))
            file, contents = cache[fname]
            new_contents = move(contents, start, size, target)
            cache[fname] = (file, mode, new_contents)
            write2file(outfile,
                       f'Move text in {fname} from {start} till {start + size} to {target} committed as transaction.')
        elif command.startswith('tr'):
            fname = tokens[1]
            size = int(tokens[2])
            if not assert_file_availability(fname, thread_id, cache, outfile, 'w'):
                continue
            file, contents = cache[fname]
            new_contents = truncate(contents, size)
            cache[fname] = (file, mode, new_contents)
            write2file(outfile,
                       f'Truncate contents of {fname} to {result} committed as transaction.')
        else:
            continue
