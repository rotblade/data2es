import unittest
import data2es


class TestData2es(unittest.TestCase):
    def setUp(self):
        csvfile = open('test.csv', newline='')
        return csvfile

    def tearDown(self):
        csvfile.close()

