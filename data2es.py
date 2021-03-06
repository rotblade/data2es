import csv
import json
import click
from elasticsearch import Elasticsearch, helpers
from utils import echo, isperiod, t2i, get_fieldnames, time_interval, index_op


def docs_from_file(filename, idx_name, doc_type, id_field_idx,
                   quiet):
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
            dict_reader = csv.DictReader(doc_file, fieldnames=fields)
            if 'ticket' in doc_type:
                fields.append("ticket_time")

            echo('Using the following ' + str(len(fields)) + ' fields:',
                 quiet)
            for field in fields:
                echo(field, quiet)

            i = 0
            for row in dict_reader:
                # Prepare meta info for each indexed document.
                meta = {
                    'index': idx_name,
                    'type': doc_type,
                }
                if id_field_idx is not None:
                    meta['id'] = row[fields[int(id_field_idx)]]
                # Convert tim inteval to an integer in minutes.
                for k, v in row.items():
                    if isinstance(v, str) and isperiod(v):
                        row[k] = t2i(v)
                if 'ticket' in doc_type:
                    row['ticket_time'] = time_interval(row['create_time'],
                                                       row['close_time'],
                                                       '%m/%d/%Y %I:%M:%S %p')
                i += 1
                echo('Sending item %s to ES ...' % i, quiet)
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
    Bulk import a delimited file into a target Elasticsearch instance.
    Common delimited files include things like CSV.

    Load a CSV file:
    data2es --index-name myindex --doc-type mydoc --import-file test.csv
    """

    echo('Using host: %s' % host, quiet)
    es = Elasticsearch(hosts=[host])

    if es.indices.exists(index_name):
        echo('Index %s already exist' % index_name, False)
        if delete_index:
            es.indices.delete(index=index_name)
            echo('Deleted: %s' % index_name, quiet)
            es.indices.create(index=index_name)
            echo('Created new index: %s' % index_name, quiet)
    else:
        es.indices.create(index=index_name)
        echo('Created new index: %s' % index_name, quiet)

    echo('Using document type: %s' % doc_type, quiet)
    if mapping_file:
        echo('Applying mapping from: %s' % mapping_file, quiet)
        with open(mapping_file) as f:
            mapping = json.loads(f.read())
        es.indices.put_mapping(doc_type, mapping, [index_name,])

    action_g = docs_from_file(import_file, index_name, doc_type,
                              id_field_idx, quiet)
    helpers.bulk(es, action_g())


if __name__ == "__main__":
    cli()

