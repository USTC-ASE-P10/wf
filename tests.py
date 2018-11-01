from itertools import product
from tempfile import NamedTemporaryFile
import unittest

from wf import main


class BaseTest(unittest.TestCase):
    options = ()

    def _run(self, *files, options=None):
        """
        Run `wf.py options files` and return the output.
        :param files: list of file contents.
        :param options: list of options.
        :return: Program output with every file path replaced with a `#`.
        """
        if options is None:
            options = self.options
        options = list(options)
        tempfiles = []
        for file in files:
            tempfile = NamedTemporaryFile('w', delete=False, encoding='utf8')
            tempfile.write(file)
            tempfile.flush()
            tempfiles.append(tempfile)
        output = ''.join(main(options + [tempfile.name for tempfile in tempfiles]))
        for tempfile in tempfiles:
            output = output.replace(tempfile.name, '#')
            tempfile.close()
        return output

    @staticmethod
    def _format(data):
        """
        Format program output.
        :param data: list of (item, count)s.
        :return: str to be compared with.
        """
        return 'File: #\n' + ''.join('%40s\t%d\n' % i for i in data) + '\n'


class TestLetterOccurrences(BaseTest):
    options = ('-c',)

    def test_1_file(self):
        for i in ('', 'a'):
            with self.subTest(i=i):
                output = self._run(i)
                expect = self._format([(i, 1)] if i else [])
                self.assertEqual(output, expect)

    def test_2_files(self):
        for i in ('', 'a', 'b'):
            for j in ('', 'a', 'b'):
                with self.subTest(i=i, j=j):
                    output = self._run(i, j)
                    expect = self._format([(i, 1)] if i else []) + self._format([(j, 1)] if j else [])
                    self.assertEqual(output, expect)

    def test_function(self):
        for i in range(4):
            for p in product(*(['abcdABCD.'] * i)):
                with self.subTest(i=i, p=p):
                    file = ''.join(p)
                    data = {(c.lower(), file.count(c.lower()) + file.count(c.upper())) for c in file if c != '.'}
                    data = sorted(data, key=lambda x: (-x[1], x[0]))
                    output = self._run(file)
                    expect = self._format(data)
                    self.assertEqual(output, expect)


class TestWordOccurrences(BaseTest):
    options = ('-f',)

    def test_1_file(self):
        for i in ('', 'a'):
            with self.subTest(i=i):
                output = self._run(i)
                expect = self._format([(i, 1)] if i else [])
                self.assertEqual(output, expect)

    def test_2_files(self):
        for i in ('', 'a', 'b'):
            for j in ('', 'a', 'b'):
                with self.subTest(i=i, j=j):
                    output = self._run(i, j)
                    expect = self._format([(i, 1)] if i else []) + self._format([(j, 1)] if j else [])
                    self.assertEqual(output, expect)

    def test_function(self):
        output = self._run('12ab@ * ajfd9ii a7j00* acx 12 acx')
        expect = self._format([('acx', 2), ('a7j00', 1), ('ajfd9ii', 1)])
        self.assertEqual(output, expect)


class TestLimit(BaseTest):
    options = ('-f',)

    def _run(self, *files, options=None, limit=None):
        if options is None:
            options = list(self.options)
        if limit is not None:
            options += ['-n', str(limit)]
        return super()._run(*files, options=options)

    def _format(self, data, limit=None):
        if limit is not None:
            data = data[:limit]
        return super()._format(data)

    def test_file(self):
        for limit in range(3):
            with self.subTest(limit=limit):
                output = self._run('1', 'a', 'a b', limit=limit)
                expect = (self._format([], limit=limit)
                          + self._format([('a', 1)], limit=limit)
                          + self._format([('a', 1), ('b', 1)], limit=limit))
                self.assertEqual(output, expect)


class TestStopwords(BaseTest):
    options = ('-f', '-x')

    def test_file(self):
        output = self._run('', '1', 'a', 'a b')
        expect = self._format([]) + self._format([('a', 1)]) + self._format([('a', 1), ('b', 1)])
        self.assertEqual(output, expect)
        output = self._run('a', '1', 'a', 'a b')
        expect = self._format([]) + self._format([]) + self._format([('b', 1)])
        self.assertEqual(output, expect)
        output = self._run('a\nc', '1', 'a', 'a b')
        self.assertEqual(output, expect)


class TestPhraseOccurrences(BaseTest):
    options = ('-f',)

    def _run(self, *files, options=None, n=None):
        if options is None:
            options = list(self.options)
        if n is not None:
            options = ['-p', str(n)]
        return super()._run(*files, options=options)

    def test_1_file(self):
        for i in ('', 'a'):
            with self.subTest(i=i):
                output = self._run(i, n=1)
                expect = self._format([(i, 1)] if i else [])
                self.assertEqual(output, expect)

    def test_2_files(self):
        for i in ('', 'a', 'b'):
            for j in ('', 'a', 'b'):
                with self.subTest(i=i, j=j):
                    output = self._run(i, j, n=1)
                    expect = self._format([(i, 1)] if i else []) + self._format([(j, 1)] if j else [])
                    self.assertEqual(output, expect)

    def test_function(self):
        output = self._run('12ab@ * ajfd9ii a7j00* acx 12 acx', n=1)
        expect = self._format([('acx', 2), ('a7j00', 1), ('ajfd9ii', 1)])
        self.assertEqual(output, expect)

    def test_phrase(self):
        output = self._run('', n=2)
        expect = self._format([])
        self.assertEqual(output, expect)
        output = self._run('a', n=2)
        expect = self._format([])
        self.assertEqual(output, expect)
        output = self._run('a b', n=2)
        expect = self._format([('a b', 1)])
        self.assertEqual(output, expect)
        output = self._run('a, b', n=2)
        expect = self._format([])
        self.assertEqual(output, expect)
        output = self._run('a b, a', n=2)
        expect = self._format([('a b', 1)])
        self.assertEqual(output, expect)
        output = self._run('a, b a b', n=2)
        expect = self._format([('a b', 1), ('b a', 1)])
        self.assertEqual(output, expect)
        output = self._run('a, b a b', n=3)
        expect = self._format([('b a b', 1)])
        self.assertEqual(output, expect)
        output = self._run('a b a b a', n=3)
        expect = self._format([('a b a', 2), ('b a b', 1)])
        self.assertEqual(output, expect)


class TestVerbs(BaseTest):
    options = ('-f', '-v')

    def test_file(self):
        output = self._run('', '1', 'a', 'a b')
        expect = self._format([]) + self._format([('a', 1)]) + self._format([('a', 1), ('b', 1)])
        self.assertEqual(output, expect)
        output = self._run('aa -> aaa,a', '1', 'a', 'a b')
        expect = self._format([]) + self._format([('aa', 1)]) + self._format([('aa', 1), ('b', 1)])
        self.assertEqual(output, expect)
        output = self._run('b -> a', '1', 'a', 'a b')
        expect = self._format([]) + self._format([('b', 1)]) + self._format([('b', 2)])
        self.assertEqual(output, expect)


class TestPitfalls(BaseTest):
    def test_1(self):
        output = self._run('hello, world', options=('-p', '2'))
        expect = self._format([])
        self.assertEqual(output, expect)

    def test_2(self):
        output = self._run("a-b.c'd.e\nf.g\rh", options=('-p', '2'))
        expect = self._format([('e f', 1), ('g h', 1)])
        self.assertEqual(output, expect)

    def test_3(self):
        output = self._run("a-b -> a-b\nc'd -> c'd", "a-b.c'd.e\nf.g\rh", options=('-p', '2', '-v'))
        expect = self._format([('a-b', 1), ("c'd", 1), ('e f', 1), ('g h', 1)])
        self.assertEqual(output, expect)

    def test_4(self):
        output = self._run('b a', options=('-f',))
        expect = self._format([('a', 1), ('b', 1)])
        self.assertEqual(output, expect)

    def test_6(self):
        tempfile = NamedTemporaryFile('w', delete=False, encoding='utf8')
        tempfile.write('b')
        tempfile.flush()
        output = self._run('a -> b', 'a b c', options=('-p', '2', '-x', tempfile.name, '-v'))
        tempfile.close()
        expect = self._format([('a c', 1)])
        self.assertEqual(output, expect)


if __name__ == '__main__':
    unittest.main()
