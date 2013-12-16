from __future__ import print_function
import argparse
import codecs
import os.path
from pkg_resources import resource_listdir, resource_string
import re
import select
import sys


EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_ARGUMENT_ERROR = 2

LICENSES = []
for f in sorted(resource_listdir(__name__, '.')):
    match = re.match(r'template-([A-Za-z0-9_]+).txt', f)
    if match:
        LICENSES.append(match.groups()[0])


# To extend language formatting support with a new language, add an item in
# LANGS dict:
# 'language_suffix':'comment_name'
# where 'language_suffix' is the suffix of your language and 'comment_name' is
# one of the comment types supported and listed in LANG_CMT:
# text : no comment
# c    : /* * */
# unix : #
# lua  : --- --

# if you want add a new comment type just add an item to LANG_CMT:
# 'comment_name':[u'string', u'string', u'string']
# where the first string open multiline comment, second string comment every
# license's line and the last string close multiline comment,
# associate your language and source file suffix with your new comment type
# how explained above.
# EXAMPLE:
# LANG_CMT = {'c':[u'/*', u'*', u'*/']}
# LANGS = {'cpp':'c'}
# (for more examples see LANG_CMT and langs dicts below)
# NOTE: unicode (u) in comment strings is required.
# FROM: <https://github.com/licenses/lice/blob/1723d6c1950ed4de2bc5e011c2f51abb4c601f9f/lice/core.py> # noqa


LANGS = {'txt': 'text', 'h': 'c', 'hpp': 'c', 'c': 'c', 'cc': 'c', 'cpp': 'c',
         'py': 'unix', 'pl': 'perl', 'sh': 'unix', 'lua': 'lua', 'rb': 'ruby',
         'js': 'c', 'java': 'java', 'f': 'fortran', 'f90': 'fortran90',
         'erl': 'erlang', 'html': 'html', 'css': 'c', 'less': 'c', 'm': 'c'}

LANG_CMT = {'text': [u'', u'', u''], 'c': [u'/*', u' *', u' */'],
            'unix': [u'', u'#', u''], 'lua': [u'--[[', u'', u'--]]'],
            'java': [u'/**', u' *', u' */'], 'perl': [u'=item', u'', u'=cut'],
            'ruby': [u'=begin', u'', u'=end'], 'fortran': [u'C', u'C', u'C'],
            'fortran90': [u'!*', u'!*', u'!*'], 'erlang': [u'%%', u'%', u'%%'],
            'html': [u'<!--', u'', u'-->']}


def warn(msg):
    print('WARNING: ' + msg, file=sys.stderr)


def error(msg, status=EXIT_ERROR):
    print('ERROR: ' + msg, file=sys.stderr)
    die(status)


def die(status=EXIT_ERROR):
    sys.exit(status)


def generate_license_header(template, context):
    """
    Generate a license header by extracting variables from the template
    and replacing them with corresponding context values.
    """
    out = template[:]

    for key in extract_vars(template):
        try:
            out = out.replace('{{ %s }}' % key, context[key])
        except KeyError:
            error('missing "%s" in context!' % key, EXIT_ARGUMENT_ERROR)
    return out


def format_license_header(header, lang):
    """
    Format a license header for the specified language.
    """
    first, most, last = LANG_CMT[lang]
    lines = header.splitlines()

    out = [first] + [most + u' ' + line for line in lines] + [last]
    out = [line.rstrip() for line in out]

    return '\n'.join(out)


def write_license_header(file, header):
    """
    Write a formatted license header to the top of an open file object, after
    an optional #! and optional encoding declaration.
    """
    def is_encoding_line(line):
        # <http://www.python.org/dev/peps/pep-0263/>
        ENCODING = ('coding=', '-*- coding:')
        return any([e in line for e in ENCODING])

    input = file.readlines()
    output = []

    if input:
        if input[0].startswith('#!'):  # shebang
            output.append(input.pop(0))
        if is_encoding_line(input[0]):  # encoding
            output.append(input.pop(0))

    output = u''.join(output) + header.strip() + u'\n' + u''.join(input)

    file.seek(0)
    file.truncate()
    file.write(output)


def load_template(license):
    """
    Load license template from the package.
    """
    return resource_string(__name__,
                           'template-%s.txt' % license).decode('utf-8')


def extract_vars(template):
    """
    Extract variables from template. Variables are enclosed in double curly
    braces.
    """
    return sorted(set(re.findall(r'\{\{ (?P<key>\w+) \}\}', template)))


def get_lang(path):
    """
    Get the "language" of a path. Currently this is determined by its
    extension.
    """
    root, ext = os.path.splitext(path)
    if ext[0] == '.':
        ext = ext[1:]
    return LANGS[ext]


def parse_context(vars):
    """
    Parse a list of KEY=VALUE pairs into a dictionary.
    """
    if vars is None:
        vars = []

    context = {}

    for v in vars:
        key, value = v.split('=')

        if key in context:
            error('"%s" specified multiple times!' % key, EXIT_ARGUMENT_ERROR)
        context[key] = value
    return context


def main(args=sys.argv[1:], stdin=sys.stdin):
    parser = argparse.ArgumentParser(
        description='Add license headers to files passed in on stdin')

    parser.add_argument(
        'license', metavar='LICENSE', choices=LICENSES,
        help='the license to add, one of %s' % ', '.join(LICENSES))

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--vars', dest='list_vars', action='store_true',
        help='list template variables for specified license')
    group.add_argument(
        '--context', metavar='KEY=VALUE', nargs='*',
        help='KEY=VALUE formatted variables to generate the license')

    args = parser.parse_args(args)

    license = args.license
    template = load_template(license)

    if args.list_vars:
        print('The %s license template contains the following variables:' %
              license)
        vars = extract_vars(template)
        for var in vars:
            print('\t' + var)
        die(EXIT_SUCCESS)

    context = parse_context(args.context)
    header = generate_license_header(template, context)

    if stdin.isatty() and not select.select([stdin], [], [], 0.0)[0]:
        # If there's no data on stdin, we error and die.
        # <http://stackoverflow.com/a/3763257/609144>
        error('No paths on stdin!')

    paths = [line.strip() for line in stdin.readlines() if line]

    if not any(paths):
        error('No paths on stdin!')

    for p in paths:
        try:
            lang = get_lang(p)
        except (KeyError, IndexError):
            warn('could not determine filetype for %s. skipping...' % p)
            continue

        formatted = format_license_header(header, lang)

        with codecs.open(p, 'r+', encoding='utf-8') as f:
            write_license_header(f, formatted)


if __name__ == '__main__':
    main()
