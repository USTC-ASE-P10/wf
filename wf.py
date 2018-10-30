#!/usr/bin/python3

import argparse
import re
from collections import defaultdict


def letter(path):
    counts = defaultdict(lambda: 0)
    with open(path, encoding='utf8') as f:
        while True:
            c = f.read(1)
            if not c:
                break
            if not c.isalpha():
                continue
            counts[c.lower()] += 1
    yield 'File: %s\n' % path
    for (k, v) in sorted(counts.items(), key=lambda i: (-i[1], i[0])):
        yield '%40s\t%d\n' % (k, v)
    yield '\n'

    
def word(path):
    counts = defaultdict(lambda: 0)
    with open(path, encoding='utf8') as f:
        pattern = re.compile(r'[a-zA-Z0-9]+')  
        s = f.read()
        result = pattern.findall(s)        
        for w in result:
            if w[0].isdigit():
                continue
            w = w.lower()
            counts[w] += 1
    yield 'File: %s\n' %path
    for (k, v) in sorted(counts.items(), key=lambda i: (-i[1], i[0])):
        yield '%40s\t%d\n' % (k, v)
    yield '\n' 

        
        


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', metavar='<path>', nargs='+', help='file to process')
    parser.add_argument('-c', dest='function', action='store_const', const='letter', help='count letter occurrences')
    parser.add_argument('-f', dest='function', action='store_const', const='word', help='count word occurrences')
    args = parser.parse_args(args)
    if args.function == 'letter':
        for path in args.paths:
            yield from letter(path)
    elif args.function == 'word':
        for path in args.paths:
            yield from word(path)
            


if __name__ == '__main__':
    from sys import argv
    for output in main(argv[1:]):
        print(output, end='')
