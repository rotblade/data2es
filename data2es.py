import csv
import json
import click
from elasticsearch import Elasticsearch, helpers
from utils import echo, get_fieldnames, index_op, index_body


def docs_from_file(filename, idx_name, doc_type, id_field_idx=None,
                   quiet=False):
    """
    Return a generator for pulling rows from a given delimited file.

    :param filename: the name of the file to read from
    :param idx_name: index name
    :param doc_type: document type
    :param doc_id: default to 'None', that means the id field will be
        generated automatically by ES. If assigned here, it's a digital,
        stands for positional index of fields list.
    :param quiet: don't output anything to the console when this is True
    """
    def all_docs():
        with open(filename, newline='') as doc_file:
            fields = get_fieldnames(doc_file)
            echo('Using the following ' + str(len(fields)) + ' fields:',
                 quiet)
            for field in fields:
                echo(field, quiet)

            dict_reader = csv.DictReader(doc_file, fieldnames=fields)
            for row in dict_reader:
                meta = {
                    'index': idx_name,
                    'type': doc_type,
                }
                if id_field_idx is not None:
                    meta['id'] = row[fields[id_field_idx]]
                yield index_op(row, meta)

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
@click.option('--id-field-idx', required=False,
              help='Which field to be document\'s ID field')
@click.option('--delete-index', is_flag=True, required=False,
              help='Delete existing index if it exists')
@click.option('--quiet', is_flag=True, required=False,
              help='Minimize console output')
def cli(host, index_name, doc_type, import_file, mapping_file,
        id_field_idx, delete_index, quiet):
    """
    Bulk import a delimited file into a target Elasticsearch instance. Common
    delimited files include things like CSV and TSV.
    \b
    Load a CSV file:
    data2es --index-name myindex --doc-type mydoc --import-file test.csv
    """

    echo('Using host: %s' % host, quiet)
    es = Elasticsearch(hosts=[host])

    if es.indices.exists(index_name):
        if delete_index:
            es.indices.delete(index=index_name)
            echo('Deleted: %s' % index_name, quiet)
        else:
            echo('Index %s already exist' % index_name, quiet)
            return

    echo('Using document type: %s' % doc_type, quiet)
    if mapping_file:
        echo('Applying mapping from: %s' % mapping_file, quiet)
        with open(mapping_file) as f:
            mapping = json.loads(f.read())
        body = index_body(doc_type, mapping)
        es.indices.create(index=index_name, body=body)
    else:
        es.indices.delete(index=index_name)
    echo('Create new index: %s' % index_name, quiet)

    action_g = docs_from_file(index_name, doc_type, id_field_idx)
    helpers.bulk(es, action_g())


if __name__ == "__main__":
    cli()

