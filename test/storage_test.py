from ..crawler import storage as s
import unittest

class WrapperFunctionalityTest(unittest.TestCase):

    def setUp(self) -> None:
        self.a = dict()
        self.b = list()
        self.c = set()
        self.a_w = s.SafeWrapper(dict())
        self.b_w = s.SafeWrapper(list())
        self.c_w = s.SafeWrapper(set())
    
    def tearDown(self) -> None:
        self.a = None
        self.b = None
        self.c = None
        self.a_w = None
        self.b_w = None
        self.c_w = None

    def test_add(self):
        self.a['test'] = 'success'
        self.a_w['test'] = 'success'
        self.assertEqual(self.a, self.a_w)
        self.assertEqual(self.a.items(), self.a_w.items())
        self.assertEqual(self.a.keys(), self.a_w.keys())
        self.b.append('test')
        self.b_w.append('test')
        self.assertEqual(self.b, self.b_w)
        self.assertEqual(self.b[0], self.b_w[0])
        self.c.add('test')
        self.c_w.add('test')
        self.assertEqual(self.c, self.c_w)
        self.assertEqual(self.c.pop(), self.c_w.pop())

    def test_iterator(self):
        for i in range(20):
            self.a[str(i)] = i
            self.a_w[str(i)] = i
            self.b.append(i)
            self.b_w.append(i)
            self.c.add(i)
            self.c_w.add(i)
        la = [i for i in self.a]
        la_w = [i for i in self.a_w]
        lb = [i for i in self.b]
        lb_w = [i for i in self.b_w]
        lc = [i for i in self.c]
        lc_w = [i for i in self.c_w]
