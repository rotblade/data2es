from datetime import datetime
import re
import csv
import click


def echo(message, quiet):
    """
    Print the given message to standard out via click
    unless quiet is True.

    :param message: the message to print out
    :param quiet: don't print the message when this is True
    """
    if not quiet:
        click.echo(message)

def isperiod(t_str):
    """
    Return true if t_str only includes digit and ':',
    false otherwise.

    :param t_str: the string to be tested
    """
    if t_str:
        l = t_str.split(':')
        if len(l) > 1 and ''.join(l).isdigit():
            return True
        return False
    else:
        return False


def t2i(t_str):
    """
    Return a integer that represents time inteval in minutes.

    :param t_str: the string to be converted
    """
    hms = t_str.split(':')
    decade = int(hms[0]) if hms[0].isdigit() else 0
    unit =int(hms[1]) if hms[1].isdigit() else 0
    i_time = decade * 60 + unit
    return i_time


def time_interval(start, end, fmt_s):
    """
    Return a integer that represents time inteval between 'start' and
    'end' in minutes.

    :param t_str: the string to be converted
    """
    try:
        interval = datetime.strptime(end, fmt_s) - datetime.strptime(start, fmt_s)
    except ValueError:
        return 0

    return int(interval.total_seconds()/60)


def str_to_esfield(raw_str):
    """
    Return a string that meets the field name requirements in ES.

    :param raw_str: the string to be converted
    """
    def f(c):
        """
        Remove all characters except alphabetic, space, hyphen
        and underscore
        """
        if c.isalpha() or c in [' ', '-', '_']:
            return c
        else:
            return ''

    new_str = raw_str.strip()
    new_str = ''.join(map(f, new_str))
    # use one '_' to join individual words.
    new_str = '_'.join(re.findall('[A-Z][A-Z]+|[a-zA-Z][a-z]*', new_str))
    return new_str.lower()


def get_fieldnames(file_obj):
    """
    Return a list that includes all field names.

    :param file_obj: one file object to be readed.
    """
    reader_obj = csv.reader(file_obj)
    # delimited file should include the field names as the first row
    fields = [str_to_esfield(item) for item in next(reader_obj)]
    return fields


def index_op(doc, meta):
    """
    Return a document-indexing operation that can be passed to
    'bulk' method.

    :arg doc: A dict mapping of fields
    :arg meta: A dict mapping of underscore-prefixed fields with special
        meaning to ES, like ``_id`` and ``_type``
    """
    def underscore_keys(d):
        """Return a dict with every key prefixed by an underscore."""
        return dict(('_%s' % k, v) for k, v in d.items())

    action = underscore_keys(meta)
    action['_source'] = doc
    return action


def index_body(doc_type, mapping=None, setting=None):
    """
    Return body that includes index seetings and mappings.

    :parma doc_type: document type
    :parma mapping: a dict that are field mapping
    :parma seeting: a dict that are index settings
    """
    body = {}
    if setting is not None:
        body['settings'] = setting
    if mapping is not None:
        d = {}
        d[doc_type] = mapping
        body['mappings'] = d

    return body

