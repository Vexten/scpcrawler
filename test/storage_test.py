# IMPORT SETUP
import sys
sys.path.append('../')
# IMPORT SETUP

from crawler.storage import SafeWrapper
import unittest

ACC_FAIL = 'Access failure on'

class WrapperFunctionalityTest(unittest.TestCase):

    def setUp(self) -> None:
        self.default = [dict(), list(), set()]
        self.wrapped = [SafeWrapper(dict()), SafeWrapper(list()), SafeWrapper(set())]
    
    def tearDown(self) -> None:
        self.default = None
        self.wrapped = None

    def fill_values(self):
        self.default[0]['test'] = 'success'
        self.default[1].append('test')
        self.default[2].add('test')
        self.wrapped[0]['test'] = 'success'
        self.wrapped[1].append('test')
        self.wrapped[2].add('test')

    def test_add(self):
        self.fill_values()
        for i in range(3):
            self.assertEqual(self.default[i], self.wrapped[i])

    def test_access(self):
        self.fill_values()
        try:
            a = self.wrapped[0]['test']
        except Exception as e:
            self.fail(ACC_FAIL + f' dict: {str(e)}')
        try:
            a = self.wrapped[1][0]
        except Exception as e:
            self.fail(ACC_FAIL + f' list: {str(e)}')
        try:
            a = self.wrapped[2].pop()
        except Exception as e:
            self.fail(ACC_FAIL + f' set: {str(e)}')

    def test_iterator(self):
        for i in range(10,30):
            self.default[0][str(i)] = i
            self.default[1].append(i)
            self.default[2].add(i)
            self.wrapped[0][str(i)] = i
            self.wrapped[1].append(i)
            self.wrapped[2].add(i)
        for j in range(3):
            a = [i for i in self.default[j]]
            b = []
            try:
                for i in self.wrapped[j]:
                    b.append(i)
            except Exception as e:
                self.fail(f'Iterator fail on {j}, {i}: {str(e)}')
            self.assertEqual(a,b)