#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""

__author__ = "Jasmyne Ford"

import sys
import argparse
import signal
import logging
import os

stay_running = True
files_logged = []
found_magic = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter()
file_handler = logging.FileHandler("dirwatcher.log")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def search_for_magic(filename, start_line, magic_string):
    """Seatches a signle file for a line containing magic text"""
    with open(filename) as f:
        content = f.readlines()
        for i in range(start_line, len(content)):
            if magic_string in content[i]:
                logger.info(f' {filename}, {i}')
        found_magic[filename] = len(content)


def watch_directory(path, magic_string, extension, interval):
    """Watches a given directory for instances of a magic text"""
    global files_logged
    global found_magic
    while stay_running:
        try:
            text_files = [f for f in os.listdir(path) if not f.startswith('.')]
        except Exception:
            logger.info('Directory {} does not exists'.format(path))

        abspath = os.path.abspath(path)
        files = os.listdir(abspath)
        for file in text_files:
            if file.endswith(extension) and file not in files_logged:
                logger.info('New file found: {}'.format(file))
                files_logged.append(file)
            if file.endswith(extension):
                full_path = os.path.join(abspath, file)
                if full_path in found_magic:
                    start_line = found_magic[full_path]
                else:
                    start_line = 0
                search_for_magic(full_path, start_line, magic_string)
        for file in files_logged:
            if file not in files:
                logger.info('File deleted: {}'.format(file))
                files_logged.remove(file)
                found_magic[file] = 0


def create_parser():
    """ creates argument parser"""
    parser = argparse.ArgumentParser(description='Watches a directory for files containing magic text')
    parser.add_argument('-i', '--int', help='Polling interval for program')
    parser.add_argument('-e', '--ext', help='Extension of file to search for',
                        default=".txt")
    parser.add_argument('path', help='Directory to be searched', default=".")
    parser.add_argument('magic', help='Magic text to be found in files')
    return parser


def signal_handler(sig_num, frame):
    global stay_running
    sigs = dict((j, k) for k, j in reversed(sorted(signal.__dict__.items()))
                if k.startswith('SIG') and not j.startswith('SIG_'))
    logger.warning('Received OS Signal: {}'.format(sigs[sig_num]))
    stay_running = False


def main(args):
    parser = create_parser()
    args = parser.parse_args()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    logger.info("Watching directory {} for files ending with {} containing magic text {}".format(args.path, args.ext, args.magic))
    watch_directory(args.path, args.magic, args.ext, args.int)


if __name__ == '__main__':
    main(sys.argv[1:])
