# -*- coding: utf-8 -*-
# Copyright (c) 2013, RedJack, LLC.
# All rights reserved.
#
# Please see the COPYING file in this distribution for license details.
"""
Tests for `lawyerup` module.
"""
import pytest


pytestmark = pytest.mark.log2exception


def test_supported_licenses():
    """
    lawyerup should support 'GPR', 'GRR', and 'generic' licenses.
    """
    from lawyerup.core import LICENSES
    assert set(LICENSES) == set(['GPR', 'GRR', 'generic'])


def test_extract_vars():
    """
    `lawyerup.core.extract_vars` should extract variables from a string,
    where variables are enclosed in double curly braces.
    """
    from lawyerup.core import extract_vars

    expected = set(['name', 'age', 'favorite_color'])
    template = """
    hello {{ name }}. your {{ age }} is
    {{ age }} and {{ favorite_color }} {{ favorite_color }}
    """

    assert set(extract_vars(template)) == expected


def test_load_template():
    """
    `lawyerup.core.load_template(LICENSE)` should return the contents of
    `lawyerup/template-LICENSE.txt`.
    """
    from lawyerup.core import load_template

    expected = '\n'.join([
        'Copyright (c) {{ year }}, {{ organization }}.',
        'All rights reserved.',
        '',
        'Please see the COPYING file in this distribution for license details.'])
    assert load_template('generic').strip() == expected


def test_format_license_header():
    from lawyerup.core import format_license_header

    header = '\n'.join(['My very first', 'license', 'header'])
    c_header = '\n'.join(['/*', ' * My very first', ' * license', ' * header',
                          ' */'])
    assert format_license_header(header, 'c') == c_header


def test_format_license_header_strips_trailing_whitespace():
    from lawyerup.core import format_license_header

    header = '\n'.join(['So    ', 'much   ', 'trailing   ', 'space   '])
    sh_header = '\n'.join(['', '# So', '# much', '# trailing', '# space', ''])

    assert format_license_header(header, 'unix') == sh_header


def test_generate_license_header():
    from lawyerup.core import generate_license_header

    template = '{{ name }} {{ age }} blah {{ name }}'
    context = {'name': 'me', 'age': '17'}
    expected = 'me 17 blah me'

    assert generate_license_header(template, context) == expected


def test_generate_license_header_missing_context_variable():
    from lawyerup.core import generate_license_header
    from test.utils import Error

    template = '{{ name }} {{ age }} blah {{ name }}'
    context = {'name': 'me'}

    with pytest.raises(Error) as e:
        out = generate_license_header(template, context)
        assert e.message == 'missing "age" in context!'
        assert out is None


def test_get_lang():
    from lawyerup.core import get_lang

    path = '/path/to/test.py'
    expected = 'unix'
    assert get_lang(path) == expected


def test_get_lang_no_ext():
    from lawyerup.core import get_lang

    path = '/path/to/no-extension'
    with pytest.raises(IndexError):
        get_lang(path)


def test_get_lang_dotfile():
    from lawyerup.core import get_lang

    path = '/path/to/.dotfile'
    with pytest.raises(IndexError):
        get_lang(path)


def test_parse_context():
    from lawyerup.core import parse_context

    vars = ['key1=val1', 'key2=val2']
    expected = {'key1': 'val1', 'key2': 'val2'}
    assert parse_context(vars) == expected


def test_parse_context_repeated_key():
    from lawyerup.core import parse_context
    from test.utils import Error

    vars = ['key1=val1', 'key1=duplicate']
    with pytest.raises(Error) as e:
        out = parse_context(vars)
        assert e.message == '"key1" specified multiple times!'
        assert out is None


def test_write_license_header():
    from io import StringIO
    from lawyerup.core import write_license_header

    header = '\n'.join(['# license', '# here'])
    file_contents = u'\n'.join([u'my', u'first', u'file'])
    f = StringIO(file_contents)

    expected_contents = '\n'.join(['# license', '# here', 'my', 'first', 'file'])

    write_license_header(f, header)
    assert f.getvalue() == expected_contents


def test_write_license_header_after_shebang_and_encoding():
    from io import StringIO
    from lawyerup.core import write_license_header

    header = '\n'.join(['# license', '# here'])
    file_contents = u'\n'.join([u'#!/shebang', u'# -*- coding: utf-8 -*-', u'',
                               u'my', u'first', u'file'])
    f = StringIO(file_contents)

    expected_contents = '\n'.join(['#!/shebang', '# -*- coding: utf-8 -*-',
                                   '# license', '# here', '',
                                   'my', 'first', 'file'])

    write_license_header(f, header)
    assert f.getvalue() == expected_contents


def test_write_license_header_to_empty_file():
    from io import StringIO
    from lawyerup.core import write_license_header

    header = '\n'.join(['# license', '# here'])
    file_contents = u'\n'.join([])
    f = StringIO(file_contents)

    expected_contents = '\n'.join(['# license', '# here', ''])

    write_license_header(f, header)
    assert f.getvalue() == expected_contents


def test_write_license_header_unicode():
    from io import StringIO
    from lawyerup.core import write_license_header

    header = '\n'.join(['# license', '# here'])
    file_contents = u'\n'.join([u'¡Hola!'])
    f = StringIO(file_contents)

    expected_contents = '\n'.join(['# license', '# here', u'¡Hola!'])

    write_license_header(f, header)
    assert f.getvalue() == expected_contents
