import csv
import unittest
from data2es import str_to_esfield, index_op


class TestOneStringFun(unittest.TestCase):
    def test_1_strconvert(self):
        self.assertEqual(str_to_esfield('This is  a-test--string.!'),
                         'this_is_a_test_string')


class TestTwoCsvFile(unittest.TestCase):
    def setUp(self):
        self.doc_file = open('test.csv', newline='')

    def tearDown(self):
        self.doc_file.close()


    def test_1_header(self):
        header = ['ticketno', 'name', 'work_title', 'job_desc']
        reader_obj = csv.reader(self.doc_file)
        # delimited file should include the field names as the first row
        fields = [str_to_esfield(item) for item in next(reader_obj)]
        self.assertEqual(len(fields), 4)
        self.assertEqual(fields, header)

    def test_2_row(self):
        dict_row = {
            'ticketno': '10002',
            'name': 'Zhang Gavin',
            'job_desc': 'aaaa_',
            'work_title': 'supervisor'
        }
        reader_obj = csv.reader(self.doc_file)
        fields = [str_to_esfield(item) for item in next(reader_obj)]
        dict_reader = csv.DictReader(self.doc_file, fields)
        self.assertEqual(next(dict_reader), dict_row)

    def test_3_action(self):
        dict_action = {
            '_index': 'qd',
            '_type': 'ticket',
            '_id': '10002',
            '_source': {
                'ticketno': '10002',
                'name': 'Zhang Gavin',
                'job_desc': 'aaaa_',
                'work_title': 'supervisor'
            }
        }
        reader_obj = csv.reader(self.doc_file)
        fields = [str_to_esfield(item) for item in next(reader_obj)]
        dict_reader = csv.DictReader(self.doc_file, fields)
        row = next(dict_reader)
        meta = {
            'index': 'qd',
            'type': 'ticket',
            'id': row[fields[0]]
        }
        self.assertEqual(index_op(row, meta), dict_action)

if __name__ == '__main__':
    unittest.main()

