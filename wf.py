#!/usr/bin/python3

import argparse
import re
import os
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


def word(path, limit, stopwords):
    """
    :param path:
    :param limit:
    :param stopwords: path
    :return:
    """
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
    if stopwords is not None:
        with open(stopwords, encoding='utf-8') as f:
            for line in f:
                counts.pop(line.strip().lower(), None)
    yield 'File: %s\n' % path
    result = sorted(counts.items(), key=lambda i: (-i[1], i[0]))
    if limit is not None:
        result = result[:limit]
    for (k, v) in result:
        yield '%40s\t%d\n' % (k, v)
    yield '\n'


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', metavar='<path>', nargs='+', help='file to process')
    parser.add_argument('-c', dest='function', action='store_const', const='letter', help='count letter occurrences')
    parser.add_argument('-f', dest='function', action='store_const', const='word', help='count word occurrences')
    parser.add_argument('-d', dest='function', action='store_const', const='dir_word',
                        help='count word occurrences in specified directory')
    parser.add_argument('-s', dest='recursive', action='store_const', const=True, default=False, help='recursive')
    parser.add_argument('-n', dest='limit', metavar='N', type=int, help='output top N lines')
    parser.add_argument('-x', dest='stopwords', metavar='<path>', help='stopwords file')
    args = parser.parse_args(args)
    if args.function == 'letter':
        for path in args.paths:
            yield from letter(path)
    elif args.function == 'word':
        for path in args.paths:
            yield from word(path, args.limit, args.stopwords)
    elif args.function == 'dir_word':
        if not args.recursive:
            for path in args.paths:
                result = os.listdir(path)
                for r in result:
                    temp_path = os.path.join(path, r)
                    if os.path.isdir(temp_path):
                        continue
                    yield from word(temp_path, args.limit, args.stopwords)
        else:
            for path in args.paths:
                for (p, _, l) in os.walk(path):
                    for i in l:
                        yield from word(os.path.join(p, i), args.limit, args.stopwords)


if __name__ == '__main__':
    from sys import argv

    for output in main(argv[1:]):
        print(output, end='')
