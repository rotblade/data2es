import csv
import json
import unittest
from utils import str_to_esfield, t2i, get_fieldnames, \
    isperiod, time_interval, index_op, index_body


class TestOneGeneralFunc(unittest.TestCase):
    def test_1_strconvert(self):
        self.assertEqual(str_to_esfield('This is  a--testString.!'),
                         'this_is_a_test_string')
    def test_2_time2integer(self):
        self.assertEqual(t2i('03:30:18'), 210)

    def test_3_istimeintev(self):
        self.assertTrue(isperiod('03:30:18'))
        self.assertFalse(isperiod('03:30:18x'))
        self.assertFalse(isperiod(''))
        self.assertFalse(isperiod('160'))
        self.assertFalse(isperiod(':'))

    def test_4_timeinterval(self):
        self.assertEqual(time_interval('1/17/2016 03:30:15 AM',
                                       '1/17/2016 03:31:45 AM',
                                       '%m/%d/%Y %I:%M:%S %p'), 1.5)
        self.assertEqual(time_interval('1/17/2016 03:30:15 AM',
                                       '1/17/2016 03:31:45 PM',
                                       '%m/%d/%Y %I:%M:%S %p'), 721.5)
        self.assertEqual(time_interval('1/aa/2016 03:30:15 AM',
                                       '',
                                       '%m/%d/%Y %I:%M:%S %p'), 0.0)



class TestTwoCsvFile(unittest.TestCase):
    def setUp(self):
        self.doc_file = open('test.csv', newline='')

    def tearDown(self):
        self.doc_file.close()


    def test_1_fieldnames(self):
        fieldnames = ['ticket_no', 'name', 'work_title', 'job_desc']
        fields = get_fieldnames(self.doc_file)
        self.assertEqual(len(fields), 4)
        self.assertEqual(fields, fieldnames)

    def test_2_row(self):
        dict_row = {
            'ticket_no': '10002',
            'name': 'Zhang Gavin',
            'job_desc': 'aaaa_',
            'work_title': 'supervisor'
        }
        fields = get_fieldnames(self.doc_file)
        dict_reader = csv.DictReader(self.doc_file, fields)
        self.assertEqual(next(dict_reader), dict_row)

    def test_3_op(self):
        dict_action = {
            '_index': 'qd',
            '_type': 'ticket',
            '_id': '10002',
            '_source': {
                'ticket_no': '10002',
                'name': 'Zhang Gavin',
                'job_desc': 'aaaa_',
                'work_title': 'supervisor'
            }
        }
        fields = get_fieldnames(self.doc_file)
        dict_reader = csv.DictReader(self.doc_file, fields)
        row = next(dict_reader)
        meta = {
            'index': 'qd',
            'type': 'ticket',
            'id': row[fields[0]]
        }
        self.assertEqual(index_op(row, meta), dict_action)

    def test_4_body(self):
        d = {
            'properties': {
                'ticket_no': {'type': 'integer'},
                'name': {'type': 'string'},
                'work_title': {'type': 'string'},
                'job_desc': {'type': 'string'}
            }
        }
        body = {
            'mappings': {
                'ticket': d
            }
        }
        with open('test.json') as f:
            mapping = json.loads(f.read())
        self.assertEqual(index_body('ticket', mapping), body)


if __name__ == '__main__':
    unittest.main()

