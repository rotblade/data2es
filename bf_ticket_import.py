import argparse
from utils import get_fieldnames


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', required=True,
                    help='File to be processed')
parser.add_argument('--field', required=True,
                    help='Field name to be inserted')
parser.add_argument('-i', '--index',
                    help='Position for the new field')
args = parser.parse_args()

with open(args.file, newline='') as f:
    fields = get_fieldnames(f)
    if args.index:
        fields.insert(args.index, args.field)
    else:
        fields.append(args.field)

