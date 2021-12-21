import threading

from util import *

lock = threading.Lock()


def thread_runner(outfile, fs, commands):
    '''
    outfile: file path of output
    fs: FileSystem object
    commands: list of commands to perform
    '''

    # filename -> (file, mode, current_contents)
    openfiles = {}
    for command in commands:
        tokens = command.split()
        if command.startswith('create'):
            fname = tokens[-1]
            fs.create(fname)
            print2file(fs, outfile)
        elif command.startswith('delete'):
            fname = tokens[-1]
            fs.delete(fname)
            print2file(fs, outfile)
        elif command.startswith('chdir'):
            dirname = tokens[-1]
            fs.chdir(dirname)
            write2file(outfile, fs.pwd())
        elif command.startswith('mv'):
            f1, f2 = tokens[1:]
            fs.mv(f1, f2)
            print2file(fs, outfile)
        elif command.startswith('pwd'):
            write2file(outfile, fs.pwd())
        elif command.startswith('print'):
            print2file(fs, outfile)
        elif command.startswith('show_memory_map'):
            showmm2file(fs, outfile)
        elif command.startswith('open'):
            fname, mode = tokens[1:]
            if mode == 'r':
                mode_msg = 'reading'
            elif mode == 'w':
                mode_msg = 'writing'
            else:
                # invalid mode
                continue
            if mode == 'w':
                # file is locked for modification
                with lock:
                    file = fs.open(fname)
                    if file:
                        openfiles[fname] = (file, mode, file.get_contents())
                        write2file(
                            outfile, f'Opened file {fname} for {mode_msg}')
            else:
                file = fs.open(fname)
                if file:
                    openfiles[fname] = (file, mode, file.get_contents())
                    write2file(outfile, f'Opened file {fname} for {mode_msg}')
        elif command.startswith('close'):
            fname = tokens[-1]
            if fname in openfiles:
                file, mode, contents = openfiles[fname]
                fs.close(fname, contents)
                write2file(
                    outfile, f'Closed file {fname} & saved any changes.')
        elif command.startswith('save'):
            dst = tokens[-1]
            fs.save(dst)
            write2file(outfile, f'Filesystem saved at {dst}')
        elif command.startswith('append'):
            fname, text = tokens[1:]
            if fname in openfiles:
                file, mode, contents = openfiles[fname]
                if mode == 'w':
                    new_contents = append(contents, text)
                    openfiles[fname] = (file, mode, new_contents)
                    write2file(
                        outfile, f'Append text {text} to {fname} committed as transaction.')
        elif command.startswith('write'):
            fname = tokens[1]
            text = tokens[2]
            pos = int(tokens[3])
            if fname in openfiles:
                file, mode, contents = openfiles[fname]
                if mode == 'w':
                    new_contents = write_at(contents, pos, text)
                    openfiles[fname] = (file, mode, new_contents)
                    write2file(
                        outfile, f'Append text {text} to {fname} committed as transaction.')
        elif command.startswith('read_from'):
            fname = tokens[1]
            start = int(tokens[2])
            size = int(tokens[3])
            if fname in openfiles:
                file, mode, _ = openfiles[fname]
                if mode == 'r':
                    result = file.read_from(start, size)
                    write2file(outfile, f'Contents of {fname}: {result}')
        elif command.startswith('read'):
            fname = tokens[1]
            if fname in openfiles:
                file, mode, _ = openfiles[fname]
                if mode == 'r':
                    result = file.read()
                    write2file(outfile, f'Contents of {fname}: {result}')
        elif command.startswith('move'):
            fname = tokens[1]
            if fname in openfiles:
                # read tokens from position 2 onwards
                # map the items in the list to integers
                # cast to tuple and unpack it
                start, size, target = tuple(map(int, tokens[2:]))
                file, mode, contents = openfiles[fname]
                if mode == 'w':
                    new_contents = move(contents, start, size, target)
                    openfiles[fname] = (file, mode, new_contents)
                    write2file(outfile,
                               f'Move text in {fname} from {start} till {start + size} to {target} committed as transaction.')
        elif command.startswith('tr'):
            fname = tokens[1]
            size = int(tokens[2])
            if fname in openfiles:
                file, mode, contents = openfiles[fname]
                if mode == 'w':
                    new_contents = truncate(contents, size)
                    openfiles[fname] = (file, mode, new_contents)
                    write2file(outfile,
                               f'Truncate contents of {fname} to {result} committed as transaction.')
        else:
            continue
