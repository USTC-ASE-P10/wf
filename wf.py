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
    result = sorted(counts.items(), key=lambda i: (-i[1], i[0]))
    if limit is not None:
        result = result[:limit]
    for (k, v) in result:
        yield '%40s\t%d\n' % (k, v)
    yield '\n'


def word(path):
    counts = defaultdict(lambda: 0)
    with open(path, encoding='utf8') as f:
        pattern = re.compile(r'(?<![a-zA-Z0-9])[a-zA-Z][a-zA-Z0-9]*')
        s = f.read()
        result = pattern.findall(s)
        for w in result:
            w = w.lower()
            counts[verbs.get(w, w)] += 1
    for w in stopwords:
        counts.pop(w, None)
    yield 'File: %s\n' % path
    result = sorted(counts.items(), key=lambda i: (-i[1], i[0]))
    if limit is not None:
        result = result[:limit]
    for (k, v) in result:
        yield '%40s\t%d\n' % (k, v)
    yield '\n'


def phrase(path):
    counts = defaultdict(lambda: 0)
    with open(path, encoding='utf8') as f:
        pattern = re.compile(r'[a-zA-Z0-9\s]+')
        word_p = re.compile(r'(?<![a-zA-Z0-9])[a-zA-Z][a-zA-Z0-9]*')
        s = f.read()
        for sen in pattern.findall(s):
            words = []
            for w in word_p.findall(sen):
                w = w.lower()
                if w not in stopwords:
                    words.append(verbs.get(w, w))
            for i in range(len(words) - phrase_len + 1):
                counts[tuple(words[i:i + phrase_len])] += 1
    yield 'File: %s\n' % path
    result = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    if limit is not None:
        result = result[:limit]
    for (k, v) in result:
        yield '%40s\t%d\n' % (' '.join(k), v)
    yield '\n'


class PhraseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, 'function', self.const)
        setattr(namespace, self.dest, values)


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', metavar='<path>', nargs='+',
                        help='File to process.')
    parser.add_argument('-f', dest='function', action='store_const', const=word,
                        help='Count word occurrences.')
    parser.add_argument('-c', dest='function', action='store_const', const=letter,
                        help='Count character occurrences.')
    parser.add_argument('-p', dest='phrase_len', action=PhraseAction, const=phrase, metavar='<len>', type=int,
                        help='Count phrase occurrences, treating any <len> contiguous words as a phrase.')
    parser.add_argument('-n', dest='limit', metavar='<num>', type=int,
                        help='Output only the top <num> items.')
    parser.add_argument('-x', dest='stopwords', metavar='<stop-words>',
                        help='Use <stop-words> as a list of stop words, which are ignored in the counting.'
                             ' Effective only with -f or -p specified.')
    parser.add_argument('-v', dest='verbs', metavar='<verb-dict>',
                        help='Use <verb-dict> as a verb dictionary that can be used with -p or -q.')
    parser.add_argument('-d', dest='directory', action='store_true',
                        help='Treat <path> as the path to a directory and operate on each file inside the directory.')
    parser.add_argument('-s', dest='recursive', action='store_true',
                        help='Recurse into sub-directories. Must be used with -d.')
    args = parser.parse_args(args)

    global phrase_len
    phrase_len = args.phrase_len

    global limit
    limit = args.limit

    global stopwords
    stopwords = set()
    if args.stopwords is not None:
        with open(args.stopwords, encoding='utf8') as f:
            for line in f:
                stopwords.add(line.strip().lower())

    global verbs
    verbs = {}
    if args.verbs:
        with open(args.verbs, encoding='utf8') as f:
            for line in f:
                verb, _, words = line.strip().partition(' -> ')
                for w in words.split(','):
                    verbs[w.lower()] = verb.lower()

    for path in args.paths:
        if args.directory:
            for (p, _, l) in os.walk(path):
                for i in l:
                    yield from args.function(i)
                if not args.recursive:
                    break
        else:
            yield from args.function(path)


if __name__ == '__main__':
    from sys import argv

    for output in main(argv[1:]):
        print(output, end='')
