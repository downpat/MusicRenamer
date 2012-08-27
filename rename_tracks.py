import os
import sys
import argparse
import itertools
import socket
import time

from pyechonest import track, config, util as echo_util

config.ECHO_NEST_API_KEY = ""


def get_file_list(dir_list, dir_path):
    file_lst = []
    for item in dir_list:
        abs_path = os.path.join(dir_path, item)
        if os.path.isdir(abs_path):
            file_lst = list(itertools.chain(file_lst, get_file_list(os.listdir(abs_path), abs_path)))
        else:
            file_lst.append(abs_path)
    return file_lst

if __name__ == "__main__":
    descrip = '''
        A simple script that uses Echo Nest to
        rename a directory of music files
    '''

    parser = argparse.ArgumentParser(description=descrip)

    parser.add_argument(
        'directory',
        default='.',
        metavar='DIR NAME',
        help='''The directory that holds the music files that
        need renamed''',
    )

    directory = parser.parse_args().directory

    dir_name = os.path.abspath(directory)
    
    try:
        dir_list = os.listdir(dir_name)
    except OSError, e:
        print e
        sys.exit()

    print "Recursively gathering all filenames..."
    file_list = get_file_list(dir_list, dir_name)

    for filename in file_list:
        print "Opening file:", filename
        dir_path, file_name = os.path.split(filename)
        if len(file_name) <= 8:
            ext = filename.split('.')[-1]
            f = open(filename)
            print "Getting track from Echo Nest..."
            try:
                music = track.track_from_file(f, ext)
            except socket.error, e:
                print 'Socket Error:', e
                print 'Sleeping...'
                time.sleep(60)
                print 'Continuing...'
                continue
            except echo_util.EchoNestAPIError, e:
                print 'API Error:', e
                print 'Sleeping...'
                time.sleep(60)
                print 'Continuing...'
                continue
            if hasattr(music, 'title'):
                new_title = music.title.replace(' ', '')
                new_filename = '%s/%s.%s' % (dir_path, new_title, ext)
                print "Renaming", filename, "to", new_filename
                try:
                    os.rename(filename, new_filename)
                except OSError, e:
                    print "OSError:", e
                    print "Filename:", filename
                    print "New Filename:", new_filename
            else:
                print "Track does not have a title. Moving on..."
        else:
            print "Track too long, doesn't need renamed."

 

