import os
# redirect output of printing
from contextlib import redirect_stdout
from pathlib import Path

# General Utilities

SEP = os.path.sep


def get_name(path):
    '''get the file's name'''
    if path == SEP:
        return SEP
    p = Path(path)
    return p.name


def get_parent(path):
    '''get the path to parent directory'''
    p = Path(path)
    parent = p.parent.absolute()
    return str(parent)


def print2file(fs, fn):
    '''fs -> FileSystem object
    fn -> file name
    '''
    with open(fn, 'a') as f:
        with redirect_stdout(f):
            fs.print()
            print()


def showmm2file(fs, fn):
    '''fs -> FileSystem object
    fn -> file name
    '''
    with open(fn, 'a') as f:
        with redirect_stdout(f):
            fs.show_mm()
            print()


def write2file(fn, txt):
    '''write text to file 'fn'''
    with open(fn, 'a') as f:
        with redirect_stdout(f):
            print(txt)

# File Writing Utilities


def append(content, text):
    '''append text to end of contents'''
    return content + text


def write_at(content, pos, text):
    '''overwrite text at pos'''
    # text before pos
    new_content = content[:pos]
    # add text at pos
    new_content += text
    # old content had text after pos + len(text) --> retain it
    if pos + len(text) < len(content):
        new_content += content[pos+len(text):]
    return new_content


def move(content, start, size, target):
    '''move contents between [start, start + size] to target'''
    if start > len(content):
        print("Start larger than contents")
        return False
    # the text to move
    move_segment = content[start:start + size]
    # add the text that comes before the segment
    new_content = content[:start]
    # add the text that comes after the segment
    # but before the target
    new_content += content[start + size:target]
    # add the segment at target position
    new_content += move_segment
    # add the remaining text
    new_content += content[target+size:]
    return new_content


def truncate(content, size):
    '''trim content to fit the size'''
    return content[:size]
