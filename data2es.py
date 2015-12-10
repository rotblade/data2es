import re
import csv
import click


def echo(message, quiet):
    '''
    Print the given message to standard out via click unless quiet is True.

    :param message: the message to print out
    :param quiet: don't print the message when this is True
    '''
    if not quiet:
        click.echo(message)


def str_to_esfield(raw_str):
    '''
    Return a string that meets the field name requirements in ES.

    :param raw_str: the string to be converted
    '''
    def f(c):
        '''
        Remove all characters except alphabetic, space, hyphen
        and underscore
        '''
        if c.isalpha() or c in [' ', '-', '_']:
            return c
        else:
            return ''

    new_str = raw_str.strip()
    new_str = ''.join(map(f, new_str))

    # use one '_' to replace successive spaces or hyphenes
    for i in [' ', '-']:
        if i in new_str:
            new_str = '_'.join(re.split(i+'+', new_str))

    return new_str.lower()


def docs_from_file(es, filename, delimiter, quiet):
    '''
    Return a generator for pulling rows from a given delimited file.

    :param es: an ElasticSearch client
    :param filename: the name of the file to read from or '-' if stdin
    :param delimiter: the delimiter to use
    :param quiet: don't output anything to the console when this is True
    '''
    def all_docs():
        with open(filename, newline='') as doc_file:
            reader_obj = csv.reader(doc_file)
            # delimited file should include the field names as the first row
            fields = [str_to_esfield(item) for item in next(reader_obj)]
            echo('Using the following ' + str(len(fields)) + ' fields:', quiet)
            for field in fields:
                echo(field, quiet)

            dict_reader = csv.DictReader(doc_file, fields)

    return all_docs


@click.command()
@click.option('--host', default='http://127.0.0.1:9200/', required=False,
              help='The Elasticsearch host (http://127.0.0.1:9200/)')
@click.option('--index-name', required=True,
              help='Index name to load data into')
@click.option('--doc-type', required=True,
              help='The document type (like user_records)')
@click.option('--import-file', required=True,
              help='File to import (or \'-\' for stdin)')
@click.option('--mapping-file', required=False,
              help='JSON mapping file for index')
@click.option('--id-field', required=False,
              help='String to be document\'s ID field')
@click.option('--delete-index', is_flag=True, required=False,
              help='Delete existing index if it exists')
@click.option('--delimiter', required=False,
              help='The field delimiter to use, defaults to CSV')
def cli(host, index_name, doc_type, import_file, mapping_file,
        id_field, delete_index, delimiter):
    pass
