import click
from utils import get_fieldnames


__version__ = '0.1'

@click.command()
@click.option('--filename', required=True,
              help='The file to get headers from')
@click.version_option(version=__version__, )
def cli(filename):
    with open(filename, newline='') as file_obj:
        headers = get_fieldnames(file_obj)
        for item in headers:
            print(item)


if __name__ == '__main__':
    cli()
