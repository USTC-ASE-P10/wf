from itertools import product
from tempfile import NamedTemporaryFile
import unittest

from wf import main


class TestLetterOccurrences(unittest.TestCase):
    @staticmethod
    def __run(*files):
        """
        Run `wf.py -c files` and return the output.
        :param files: list of file contents.
        :return: Program output with every file path replaced with a `#`.
        """
        tempfiles = []
        for file in files:
            tempfile = NamedTemporaryFile('w', delete=False, encoding='utf8')
            tempfile.write(file)
            tempfile.flush()
            tempfiles.append(tempfile)
        output = ''.join(main(['-c'] + [tempfile.name for tempfile in tempfiles]))
        for tempfile in tempfiles:
            output = output.replace(tempfile.name, '#')
            tempfile.close()
        return output

    @staticmethod
    def __format(data):
        """
        Format program output.
        :param data: list of (item, count)s.
        :return: str to be compared with.
        """
        return 'File: #\n' + ''.join('%40s\t%d\n' % i for i in data) + '\n'

    def test_1_file(self):
        for i in ('', 'a'):
            with self.subTest(i=i):
                output = self.__run(i)
                expect = self.__format([(i, 1)] if i else [])
                self.assertEqual(output, expect)

    def test_2_files(self):
        for i in ('', 'a', 'b'):
            for j in ('', 'a', 'b'):
                with self.subTest(i=i, j=j):
                    output = self.__run(i, j)
                    expect = self.__format([(i, 1)] if i else []) + self.__format([(j, 1)] if j else [])
                    self.assertEqual(output, expect)

    def test_function(self):
        for i in range(4):
            for p in product(*(['abcdABCD.'] * i)):
                with self.subTest(i=i, p=p):
                    file = ''.join(p)
                    data = {(c.lower(), file.count(c.lower()) + file.count(c.upper())) for c in file if c != '.'}
                    data = sorted(data, key=lambda x: (-x[1], x[0]))
                    output = self.__run(file)
                    expect = self.__format(data)
                    self.assertEqual(output, expect)


class TestWordOccurrences(unittest.TestCase):
    @staticmethod
    def __run(*files):
        """
        Run `wf.py -f files` and return the output.
        :param files: list of file contents.
        :return: Program output with every file path replaced with a `#`.
        """
        tempfiles = []
        for file in files:
            tempfile = NamedTemporaryFile('w', delete=False, encoding='utf8')
            tempfile.write(file)
            tempfile.flush()
            tempfiles.append(tempfile)
        output = ''.join(main(['-f'] + [tempfile.name for tempfile in tempfiles]))
        for tempfile in tempfiles:
            output = output.replace(tempfile.name, '#')
            tempfile.close()
        return output

    @staticmethod
    def __format(data):
        """
        Format program output.
        :param data: list of (item, count)s.
        :return: str to be compared with.
        """
        return 'File: #\n' + ''.join('%40s\t%d\n' % i for i in data) + '\n'

    def test_1_file(self):
        for i in ('', 'a'):
            with self.subTest(i=i):
                output = self.__run(i)
                expect = self.__format([(i, 1)] if i else [])
                self.assertEqual(output, expect)

    def test_2_files(self):
        for i in ('', 'a', 'b'):
            for j in ('', 'a', 'b'):
                with self.subTest(i=i, j=j):
                    output = self.__run(i, j)
                    expect = self.__format([(i, 1)] if i else []) + self.__format([(j, 1)] if j else [])
                    self.assertEqual(output, expect)

    def test_function(self):
        output = self.__run('12ab@ * ajfd9ii a7j00* acx 12 acx')
        expect = self.__format([('acx', 2), ('a7j00', 1), ('ajfd9ii', 1)])
        self.assertEqual(output, expect)


if __name__ == '__main__':
    unittest.main()
